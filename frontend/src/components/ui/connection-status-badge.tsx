import { useState } from 'react';
import { usePusher } from '@/contexts/PusherContext';
import { cn } from '@/lib/utils';
import { 
  Loader2, 
  Wifi, 
  WifiOff, 
  Server, 
  Database, 
  RefreshCw,
  CheckCircle2,
  XCircle,
  AlertCircle
} from 'lucide-react';
import { 
  Tooltip, 
  TooltipContent, 
  TooltipProvider, 
  TooltipTrigger 
} from '@/components/ui/tooltip';
import { 
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Button } from '@/components/ui/button';
import { formatDistanceToNow } from 'date-fns';
import { Badge } from '@/components/ui/badge';



interface ConnectionStatusBadgeProps {
  className?: string;
  mode?: 'tooltip' | 'popover';
}

export function ConnectionStatusBadge({ 
  className,
  mode = 'tooltip' 
}: ConnectionStatusBadgeProps) {
  const { status, lastPing, healthStatus, reconnect, checkHealth } = usePusher();
  const [isChecking, setIsChecking] = useState(false);

  // Format the last ping time
  const lastPingText = lastPing 
    ? `${formatDistanceToNow(lastPing, { addSuffix: true })}`
    : 'Never';

  // Handle manual health check
  const handleCheckHealth = async () => {
    setIsChecking(true);
    await checkHealth();
    setTimeout(() => setIsChecking(false), 500);
  };

  // Get status icon based on connection status
  const getStatusIcon = () => {
    if (status === 'connected') return <Wifi size={16} />;
    if (status === 'connecting') return <Loader2 size={16} className="animate-spin" />;
    return <WifiOff size={16} />;
  };

  // Get status color based on connection status
  const getStatusColor = () => {
    if (status === 'connected') return 'text-green-500 hover:text-green-600';
    if (status === 'connecting') return 'text-yellow-500 hover:text-yellow-600';
    return 'text-red-500 hover:text-red-600';
  };

  // Get health status badge
  const getHealthBadge = () => {
    if (!healthStatus) return null;
    
    if (healthStatus.status === 'healthy') {
      return (
        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
          <CheckCircle2 size={12} className="mr-1" />
          Healthy
        </Badge>
      );
    }
    
    if (healthStatus.status === 'degraded') {
      return (
        <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">
          <AlertCircle size={12} className="mr-1" />
          Degraded
        </Badge>
      );
    }
    
    return (
      <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
        <XCircle size={12} className="mr-1" />
        Unhealthy
      </Badge>
    );
  };

  // Get component status icon
  const getComponentIcon = (status: string) => {
    if (status === 'connected') return <CheckCircle2 size={14} className="text-green-500" />;
    if (status === 'degraded') return <AlertCircle size={14} className="text-yellow-500" />;
    return <XCircle size={14} className="text-red-500" />;
  };

  // Get component icon based on component type
  const getComponentTypeIcon = (type: string) => {
    if (type === 'database') return <Database size={14} />;
    if (type === 'server') return <Server size={14} />;
    return <Server size={14} />;
  };

  // Content to display in tooltip/popover
  const StatusContent = () => (
    <div className="space-y-3 w-60">
      <div className="flex items-center justify-between">
        <h4 className="font-medium text-sm">Server Connection</h4>
        {getHealthBadge()}
      </div>
      
      <div className="text-sm space-y-1">
        <div className="flex justify-between items-center">
          <span className="text-muted-foreground">Status:</span>
          <span className={cn(
            "capitalize font-medium",
            status === 'connected' ? 'text-green-500' : 
            status === 'connecting' ? 'text-yellow-500' : 
            'text-red-500'
          )}>
            {status}
          </span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-muted-foreground">Last ping:</span>
          <span>{lastPingText}</span>
        </div>
      </div>
      
      {healthStatus && (
        <div className="pt-2 border-t border-border">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium">Components</span>
            <Button 
              variant="ghost" 
              size="icon" 
              className="h-6 w-6" 
              onClick={handleCheckHealth}
              disabled={isChecking}
            >
              <RefreshCw size={14} className={cn("text-muted-foreground", isChecking && "animate-spin")} />
            </Button>
          </div>
          
          <div className="text-xs space-y-1.5">
            {Object.entries(healthStatus.components).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  {getComponentTypeIcon(key)}
                  <span className="capitalize">{key}</span>
                </div>
                <div className="flex items-center">
                  {getComponentIcon(value)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {status === 'disconnected' && (
        <Button size="sm" onClick={reconnect} className="w-full">
          Reconnect
        </Button>
      )}
    </div>
  );

  // Render badge with tooltip or popover based on mode
  if (mode === 'tooltip') {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div 
              className={cn(
                "flex items-center justify-center w-8 h-8 rounded-full cursor-pointer",
                getStatusColor(),
                className
              )}
              onClick={() => status === 'disconnected' && reconnect()}
            >
              {getStatusIcon()}
            </div>
          </TooltipTrigger>
          <TooltipContent side="bottom" align="end" className="p-4">
            <StatusContent />
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return (
    <Popover>
      <PopoverTrigger asChild>
        <div 
          className={cn(
            "flex items-center justify-center w-8 h-8 rounded-full cursor-pointer",
            getStatusColor(),
            className
          )}
        >
          {getStatusIcon()}
        </div>
      </PopoverTrigger>
      <PopoverContent side="bottom" align="end" className="p-4 w-auto">
        <StatusContent />
      </PopoverContent>
    </Popover>
  );
}