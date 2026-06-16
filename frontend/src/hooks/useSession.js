import { useState } from "react";

export function useSession() {
  const [sessionId, setSessionId] = useState(null);
  return { sessionId, setSessionId };
}
