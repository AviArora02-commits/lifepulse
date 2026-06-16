import { useEffect, useRef } from "react";

export function useWebSocket(url, onMessage) {
  const socket = useRef(null);
  useEffect(() => {
    socket.current = new WebSocket(url);
    socket.current.onmessage = (event) => onMessage?.(event.data);
    return () => socket.current?.close();
  }, [url]);
  return socket;
}
