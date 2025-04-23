import { usePusher } from '@/contexts/PusherContext';
import { cn } from '@/lib/utils';
import { Loader2, Wifi, WifiOff } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { formatDistanceToNow } from 'date-fns';

interface ConnectionStatusBadgeProps {
  className?: string;
}

export function ConnectionStatusBadge({ className }: ConnectionStatusBadgeProps) {
  const { status, lastPing, reconnect } = usePusher();

  // Format the last ping time
  const lastPingText = lastPing 
    ? `Last server ping: ${formatDistanceToNow(lastPing, { addSuffix: true })}`
    : 'No connection to server yet';

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div 
            className={cn(
              "flex items-center justify-center w-8 h-8 rounded-full cursor-pointer",
              status === 'connected' ? 'text-green-500 hover:text-green-600' : 
              status === 'connecting' ? 'text-yellow-500 hover:text-yellow-600' : 
              'text-red-500 hover:text-red-600',
              className
            )}
            onClick={() => status === 'disconnected' && reconnect()}
          >
            {status === 'connected' && <Wifi size={16} />}
            {status === 'connecting' && <Loader2 size={16} className="animate-spin" />}
            {status === 'disconnected' && <WifiOff size={16} />}
          </div>
        </TooltipTrigger>
        <TooltipContent>
          <div>
            <div>{status === 'connected' ? 'Connected to server' : 
                 status === 'connecting' ? 'Connecting to server...' : 
                 'Disconnected from server (click to reconnect)'}</div>
            <div className="text-xs text-muted-foreground mt-1">{lastPingText}</div>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}