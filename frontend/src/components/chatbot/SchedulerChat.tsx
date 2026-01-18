import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2, Terminal, X } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useQuery } from "@tanstack/react-query";
import logo from "../../assets/plane_logo.png";

interface Message {
    role: "user" | "assistant";
    content: string;
}

interface SchedulerChatProps {
    uuid: string;
}

interface StatusData {
    status: string;
}

export default function SchedulerChat({ uuid }: SchedulerChatProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [isOpen, setIsOpen] = useState(false);
    const [schedulingData, setSchedulingData] = useState<any>(null);

    const scrollEndRef = useRef<HTMLDivElement>(null);
    const scrollToBottom = () => {
        scrollEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    const { data: statusData } = useQuery<StatusData>({
        queryKey: ["jobStatus", uuid],
        queryFn: async () => {
            const response = await fetch(`http://localhost:8000/job_status/${uuid}`);
            if (!response.ok) throw new Error("Status check failed");
            return response.json();
        },
        enabled: !!uuid && !schedulingData,
        refetchInterval: (query) =>
            query.state.data?.status === "completed" ? false : 2000,
    });

    useEffect(() => {
        const fetchSchedulingData = async () => {
            if (!uuid || statusData?.status !== "completed") return;

            setIsLoading(true);
            try {
                const response = await fetch(`http://localhost:8000/compare_flights/${uuid}/ai`);
                if (!response.ok) {
                    throw new Error(`Failed to fetch schedule for job ${uuid}`);
                }
                const data = await response.json();
                setSchedulingData(data);
            } catch (error) {
                setMessages(prev => [
                    ...prev,
                    {
                        role: "assistant",
                        content: `CRITICAL: Unable to fetch scheduling data for job ${uuid}.`
                    }
                ]);
            } finally {
                setIsLoading(false);
            }
        };

        fetchSchedulingData();
    }, [uuid, statusData?.status]);

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = { role: "user", content: input };
        const cleanHistory = messages.filter(m => !m.content.includes("CRITICAL: Secure link"));

        setMessages(prev => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            const response = await fetch("http://localhost:8000/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    history: cleanHistory,
                    new_message: input,
                    scheduling_data: schedulingData,
                }),
            });

            if (!response.ok) {
                const errorBody = await response.json();
                console.error("FastAPI Validation Error:", errorBody);
                throw new Error("Connection failed");
            }

            const data = await response.json();
            setMessages(prev => [...prev, { role: "assistant", content: data.response }]);
        } catch (error) {
            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: "CRITICAL: Secure link to AI scheduler severed. Check local backend."
                }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) {
        return (
            <div className="relative">
                <img
                    src={logo}
                    alt="Open AI Scheduler Chat"
                    onClick={() => setIsOpen(true)}
                    className="absolute bottom-0 left-0 h-25 w-auto cursor-pointer transition-transform opacity-80 duration-300 hover:scale-105 active:scale-95"
                />
            </div>
        );
    }

    return (
        <div className="w-80 h-96 origin-bottom animate-in fade-in slide-in-from-bottom duration-300">
            <Card className="w-full h-full flex flex-col shadow-2xl border-zinc-800 bg-zinc-950/50 backdrop-blur-md text-zinc-50 overflow-hidden">
                <CardHeader className="py-3 px-4 border-b border-zinc-900 flex-none">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Terminal size={16} className="text-blue-500" />
                            <CardTitle className="text-lg font-bold tracking-tight text-white">
                                AI Scheduler Help
                            </CardTitle>
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="!bg-transparent border-none p-0 text-zinc-500 hover:text-white transition-colors outline-none"
                        >
                            <X size={18} />
                        </button>
                    </div>
                </CardHeader>

                <CardContent className="flex-1 min-h-0 p-0 flex flex-col overflow-hidden">
                    <ScrollArea className="flex-1 w-full h-full">
                        <div className="p-4 flex flex-col gap-4">
                            {messages.length === 0 && (
                                <div className="flex flex-col items-center justify-center py-10 text-center opacity-20">
                                    <Bot size={32} className="mb-2" />
                                    <p className="text-[10px] font-mono uppercase tracking-widest">
                                        Any flight inquiries?
                                    </p>
                                </div>
                            )}

                            {messages.map((msg, i) => (
                                <div
                                    key={i}
                                    className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}
                                >
                                    <div
                                        className={`mt-1 h-7 w-7 rounded border flex items-center justify-center shrink-0 
                                        ${msg.role === "user"
                                                ? "bg-zinc-800 border-zinc-700"
                                                : "bg-blue-500/10 border-blue-500/30"}`}
                                    >
                                        {msg.role === "user"
                                            ? <User size={12} className="text-zinc-400" />
                                            : <Bot size={12} className="text-blue-400" />}
                                    </div>
                                    <div
                                        className={`rounded-xl px-3 py-2 text-xs leading-relaxed max-w-[85%]
                                        ${msg.role === "user"
                                                ? "bg-zinc-800/50 text-zinc-200 whitespace-pre-wrap"
                                                : "bg-blue-500/5 border border-blue-500/10 text-blue-50"}`}
                                    >
                                        {/* Logic to handle assistant points via new lines */}
                                        {msg.role === "assistant" ? (
                                            <ul className="space-y-1 list-none">
                                                {msg.content.split("\n").filter(line => line.trim() !== "").map((line, index) => (
                                                    <li key={index} className="flex gap-2">
                                                        <span className="text-blue-500 shrink-0">•</span>
                                                        <span>{line.trim()}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        ) : (
                                            msg.content
                                        )}
                                    </div>
                                </div>
                            ))}

                            {(isLoading || (statusData && statusData.status !== "completed")) && (
                                <div className="flex gap-3 flex-row items-center animate-pulse">
                                    <div className="h-7 w-7 rounded border border-blue-500/30 bg-blue-500/10 flex items-center justify-center">
                                        <Loader2 size={12} className="animate-spin text-blue-400" />
                                    </div>
                                    <div className="bg-blue-500/5 border border-blue-500/10 rounded-xl px-4 py-2 text-[10px] text-blue-400 font-mono italic">
                                        {statusData?.status !== "completed" ? "Calculating Optimizations..." : "Analyzing Schedule..."}
                                    </div>
                                </div>
                            )}

                            <div ref={scrollEndRef} className="h-px w-full" />
                        </div>
                    </ScrollArea>

                    <div className="p-5 border-t border-zinc-900 bg-zinc-950/40 backdrop-blur-sm flex-none">
                        <div className="relative flex items-center">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                                placeholder="Query AI scheduler..."
                                className="w-full bg-zinc-950 border border-zinc-800 rounded pl-3 pr-10 py-2 text-xs outline-none 
                                    transition-all focus:border-blue-500/50 placeholder:text-zinc-700 text-zinc-100"
                            />
                            <button
                                onClick={handleSend}
                                disabled={isLoading || !input.trim() || !schedulingData}
                                className="absolute right-0 text-blue-500 hover:text-blue-400 disabled:text-zinc-800 transition-colors"
                            >
                                <Send size={16} />
                            </button>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}