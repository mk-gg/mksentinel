import sys
import selfcord
from selfcord.ext import commands
import asyncio
import functools
import json
import re
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict
from dataclasses import dataclass
from urllib.parse import urlparse
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from src.utils import translate_confusable_characters


from src.config import Config

server_bots = {
    396548639641567232,  # Mavis Market Bot (new)
    1110593454012104745, # Mavis Market Bot
    823695836319055883,  # AxieBot 
    1230221894221824222, # Axie.Bot [App]
    1217477415757025444, # EndlessHerald [Axie Infinity]
}


@dataclass
class MessageSignature:
    """Store key characteristics of messages"""
    monetary_patterns: bool
    urls_present: Set[str]
    contact_info: bool
    urgency_indicators: bool
    common_tokens: Set[str]
    embedding: np.ndarray = None


#cogs/scam_message.py
class MessageParse(commands.Cog):
    def __init__(self, client, database_path: str = 'src/files/scam_database.json'):
        self.client = client
        self.database_path = database_path
        self.model = None
        self.model_lock = asyncio.Lock()
        self.message_categories = defaultdict(list)
        
        # Load database right away
        self.scam_database = self._load_database()
        self.known_domains = set(self.scam_database.get('domains', []))
        
        # Initialize patterns
        self.monetary_pattern = re.compile(r'(?:[\$€£¥]|\d+k?\s*(?:usd|eur|gbp|jpy))', re.IGNORECASE)
        self.contact_pattern = re.compile(r'(?:telegram|whatsapp|dm|pm|contact|message)', re.IGNORECASE)
        self.urgency_words = {'hurry', 'quick', 'fast', 'limited', 'exclusive', 'now', 'urgent', 'don\'t miss'}
        self.similarity_threshold = 0.8


    def _load_database(self) -> Dict:
        """Load and parse the JSON database"""
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Loaded database with {len(data.get('messages', []))} messages and {len(data.get('domains', []))} domains")
                return data
        except FileNotFoundError:
            print(f"Warning: Database file {self.database_path} not found. Creating empty database.")
            return {'messages': [], 'domains': []}
        except json.JSONDecodeError:
            print(f"Error: Database file {self.database_path} is not valid JSON.")
            return {'messages': [], 'domains': []}

    def _save_database(self):
        """Save the current database to file"""
        with open(self.database_path, 'w', encoding='utf-8') as f:
            json.dump({
                'messages': self.scam_database['messages'],
                'domains': list(self.known_domains)
            }, f, indent=2)

    async def load_model(self):
        """Lazily load the sentence transformer model"""
        if self.model is None:
            async with self.model_lock:
                if self.model is None:
                    self.model = await asyncio.get_event_loop().run_in_executor(
                        None,
                        functools.partial(SentenceTransformer, 'all-MiniLM-L6-v2')
                    )

    async def _get_embedding(self, text: str) -> np.ndarray:
        """Get sentence embedding for text"""
        await self.load_model()
        return await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.model.encode([text])[0]
        )

    def _calculate_semantic_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        return float(cosine_similarity(
            embedding1.reshape(1, -1),
            embedding2.reshape(1, -1)
        )[0][0])

    def _extract_urls(self, text: str) -> Set[str]:
        """Extract and normalize URLs from text"""
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        normalized_urls = set()
        for url in urls:
            try:
                parsed = urlparse(url)
                normalized_urls.add(parsed.netloc.lower())
            except:
                continue
        return normalized_urls

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text while preserving important patterns"""
        # Preserve URLs for separate analysis
        urls = self._extract_urls(text)
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove emoji and special characters but keep basic punctuation and numbers
        text = re.sub(r'[^\w\s.,!?$€£¥]', '', text)
        
        # Convert to lowercase and normalize spaces
        text = ' '.join(text.lower().split())
        return text

    async def _get_signature(self, text: str) -> MessageSignature:
        """Extract key characteristics and embedding from a message"""
        urls = self._extract_urls(text)
        tokens = set(self._preprocess_text(text).split())
        
        # Get semantic embedding
        embedding = await self._get_embedding(self._preprocess_text(text))
        
        return MessageSignature(
            monetary_patterns=bool(self.monetary_pattern.search(text)),
            urls_present=urls,
            contact_info=bool(self.contact_pattern.search(text)),
            urgency_indicators=bool(tokens.intersection(self.urgency_words)),
            common_tokens=tokens,
            embedding=embedding
        )

    def _compare_signatures(self, sig1: MessageSignature, sig2: MessageSignature) -> float:
        """Compare two message signatures for similarity"""
        score = 0.0
        total_checks = 4
        
        # Check patterns
        if sig1.monetary_patterns == sig2.monetary_patterns:
            score += 1.0
        if sig1.urls_present.intersection(sig2.urls_present):
            score += 1.0
        if sig1.contact_info == sig2.contact_info:
            score += 1.0
        if sig1.urgency_indicators == sig2.urgency_indicators:
            score += 1.0
            
        return score / total_checks

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using SequenceMatcher"""
        return SequenceMatcher(None, text1, text2).ratio()

    def _get_patterns(self, signature: MessageSignature) -> List[str]:
        """Get list of detected patterns from signature"""
        patterns = []
        if signature.monetary_patterns:
            patterns.append('monetary')
        if signature.urls_present:
            patterns.append('urls')
        if signature.contact_info:
            patterns.append('contact')
        if signature.urgency_indicators:
            patterns.append('urgency')
        return patterns

    async def analyze_message(self, message: str,
                          min_signature_similarity: float = 0.5,
                          min_semantic_similarity: float = 0.7) -> Dict:
        """
        Analyze message for suspicious patterns and similarity to known patterns.
        
        Args:
            message (str): Message to analyze
            min_signature_similarity (float): Minimum pattern match threshold
            min_semantic_similarity (float): Minimum semantic similarity threshold
            
        Returns:
            Dict: Analysis results including similarity scores and matched patterns
        """
        try:
            await self.load_model()
          
            processed_message = self._preprocess_text(message)
            message_signature = await self._get_signature(message)
            matches = []
            
            # Initialize analysis result
            analysis = {
                'similarity': 0.0,
                'patterns_detected': self._get_patterns(message_signature),
                'flags': set(),
                'matched_category': None
            }
            
            # Check for known malicious domains
            if message_signature.urls_present.intersection(self.known_domains):
                analysis['similarity'] = 1.0
                analysis['flags'].add('malicious_url')
                analysis['matched_category'] = 'known_malicious_domain'
                return analysis
            
            # Check against all categories
            for category, messages in self.message_categories.items():
                for scam_msg in messages:
                    text_similarity = self._calculate_similarity(
                        processed_message,
                        scam_msg['processed_text']
                    )
                    
                    semantic_similarity = self._calculate_semantic_similarity(
                        message_signature.embedding,
                        scam_msg['signature'].embedding
                    )
                    
                    sig_similarity = self._compare_signatures(
                        message_signature,
                        scam_msg['signature']
                    )
                    
                    combined_similarity = (
                        text_similarity * 0.3 +
                        semantic_similarity * 0.4 +
                        sig_similarity * 0.3
                    )
                    
                    if (sig_similarity >= min_signature_similarity and
                        semantic_similarity >= min_semantic_similarity and
                        combined_similarity >= self.similarity_threshold):
                        
                        matches.append({
                            'similarity': combined_similarity,
                            'category': category,
                            'flags': scam_msg['flags']
                        })
            
            # Update analysis with best match if found
            if matches:
                best_match = max(matches, key=lambda x: x['similarity'])
                analysis['similarity'] = best_match['similarity']
                analysis['flags'].update(best_match['flags'])
                analysis['matched_category'] = best_match['category']
            
            # Add basic pattern flags
            if message_signature.monetary_patterns:
                analysis['flags'].add('contains_monetary')
            if message_signature.contact_info:
                analysis['flags'].add('contact_solicitation')
            if message_signature.urgency_indicators:
                analysis['flags'].add('urgency_tactics')
            
            return analysis
            
        except Exception as e:
            print(f"Error in analyze_message: {str(e)}")
            return None

    async def _preprocess_database(self):
        """Initialize message categories from database"""
        for message in self.scam_database['messages']:
            processed_text = self._preprocess_text(message['text'])
            signature = await self._get_signature(message['text'])
            
            self.message_categories[message['category']].append({
                'processed_text': processed_text,
                'original_text': message['text'],
                'flags': message['flags'],
                'signature': signature
            })

    async def is_similar(self, message):
        processed_text = translate_confusable_characters(message)
        analysis = await self.analyze_message(processed_text)
        if analysis and (analysis['similarity'] >= self.similarity_threshold):
            response = (
                "⚠️ **Suspicious Message Detected**\n\n"
                f"**Confidence:** {analysis['similarity']*100:.1f}%\n"
                f"**Category:** {analysis['matched_category'] or 'Unknown'}\n"
                f"**Patterns:** {', '.join(analysis['patterns_detected'])}\n"
                f"**Risk Flags:** {', '.join(analysis['flags'])}"
            )
            
            print(f"Response: {response}")  # For logging
            return True
        return False


    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if message.guild is None:
    #         return  # Ignore DMs

    #     """Analyze messages as they come in"""
    #     if str(message.guild.id) not in Config.guilds:
    #         return
    #     # Ignore Server bots
    #     if message.author.id in server_bots:
    #         return
        
    #     try:
    #         if message.type == selfcord.MessageType.auto_moderation_action:
    #             for embed in message.embeds:
    #                 embed_dict = embed.to_dict()
    #                 sent_message = embed_dict.get('description', '')
    #         else:
    #             sent_message = message.content
            
            
    #     except Exception as e:
    #         print(e)
        
        
    #     processed_text = translate_confusable_characters(sent_message)
    #     analysis = await self.analyze_message(processed_text)
    #     if analysis and (analysis['similarity'] >= self.similarity_threshold):
    #         response = (
    #             "⚠️ **Suspicious Message Detected**\n\n"
    #             f"**Confidence:** {analysis['similarity']*100:.1f}%\n"
    #             f"**Category:** {analysis['matched_category'] or 'Unknown'}\n"
    #             f"**Patterns:** {', '.join(analysis['patterns_detected'])}\n"
    #             f"**Risk Flags:** {', '.join(analysis['flags'])}"
    #         )
    #         try:
    #             await message.add_reaction('⚠️')
    #         except Exception as e:
    #             print(e)
                
    #         moderation_cog = self.client.get_cog('Moderation')
    #         if moderation_cog:
    #             data = {
    #                 'guild': message.guild,
    #                 'member': message.author,
    #                 'message': sent_message, #If the message is not included, send_panel will not be called.
    #                 'reason': "Scam Attempt",
    #                 'message_obj': message
    #             }
                
    #             await moderation_cog.ban_user(data, reason="Scam Attempt", send_panel_to_channel=True, delete_message_seconds=3600)
                
     
    #         else:
    #             print(f"Moderation cog not found.")
    #         print(response)  # For logging
            # await message.channel.send(response)  # Uncomment to send to channel


    @commands.command(name="test_timeout")
    async def test_to(self, ctx):
        if ctx.message.author.id != self.client.user.id:
            return
        


        moderation_cog = self.client.get_cog('Moderation')
        if moderation_cog:
            guild = self.client.get_guild(438327036205858818)
            member = guild.get_member(1022068533326250065)


            data = {
                'guild': guild,
                'member': member,
                'message': '', #If the message is not included, send_panel will not be called.
                'reason': "Scam Attempt"
            }

            await moderation_cog.timeout_user(data, reason="Test", timeout_duration=60)
            
    
        else:
            print(f"Moderation cog not found.")


    @commands.command(name="analyze")
    async def analyze_command(self, ctx, *, text: str):
        """Command to manually analyze a message"""
        if ctx.message.author.id != self.client.user.id:
            return
        processed_text = translate_confusable_characters(text)
        analysis = await self.analyze_message(processed_text, min_semantic_similarity=0.3)
        print(text)
        if analysis:
            response = (
                "🔍 **Message Analysis Results**\n\n"
                f"**Similarity Score:** {analysis['similarity']*100:.1f}%\n"
                f"**Category:** {analysis['matched_category'] or 'Unknown'}\n"
                f"**Detected Patterns:** {', '.join(analysis['patterns_detected'])}\n"
                f"**Risk Flags:** {', '.join(analysis['flags'])}\n"
                "\n**Detection Details:**\n"
            )
            
            # Add individual similarity scores if available
            if 'text_similarity' in analysis:
                response += f"- Text Similarity: {analysis['text_similarity']*100:.1f}%\n"
            if 'semantic_similarity' in analysis:
                response += f"- Semantic Similarity: {analysis['semantic_similarity']*100:.1f}%\n"
            if 'signature_similarity' in analysis:
                response += f"- Pattern Matching: {analysis['signature_similarity']*100:.1f}%\n"
                
            await ctx.send(response)
        else:
            await ctx.send("✅ No suspicious patterns detected.")

    @commands.command(name="add_domain")
    @commands.has_permissions(administrator=True)
    async def add_domain(self, ctx, domain: str):
        """Add a domain to the known suspicious domains list"""
        if ctx.message.author.id != self.client.user.id:
            return
        domain = domain.lower()
        if domain not in self.known_domains:
            self.known_domains.add(domain)
            self._save_database()
            await ctx.send(f"Added `{domain}` to suspicious domains list.")
        else:
            await ctx.send(f"`{domain}` is already in the suspicious domains list.")

    @commands.command(name="remove_domain")
    async def remove_domain(self, ctx, domain: str):
        """Remove a domain from the known suspicious domains list"""
        if ctx.message.author.id != self.client.user.id:
            return
        domain = domain.lower()
        if domain in self.known_domains:
            self.known_domains.remove(domain)
            self._save_database()
            await ctx.send(f"Removed `{domain}` from suspicious domains list.")
        else:
            await ctx.send(f"`{domain}` is not in the suspicious domains list.")

    @commands.command(name="list_domains")
    async def list_domains(self, ctx):
        """List all known suspicious domains"""
        if ctx.message.author.id != self.client.user.id:
            return
        if self.known_domains:
            domains_list = "\n".join(sorted(self.known_domains))
            await ctx.send(f"**Known Suspicious Domains:**\n```\n{domains_list}\n```")
        else:
            await ctx.send("No suspicious domains are currently listed.")

   

async def setup(client):
    cog = MessageParse(client)
    await cog.load_model()  # Pre-load the model
    await cog._preprocess_database()  # Initialize database
    await client.add_cog(cog)