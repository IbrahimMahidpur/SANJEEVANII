import React from "react";

// --- SVG ICONS ---
const EditIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24" {...props}><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" /><path d="m15 5 4 4" /></svg>
);
const SearchIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24" {...props}><circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></svg>
);
const LibraryIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24" {...props}><rect x="3" y="4" width="18" height="16" rx="2" /><path d="M7 4v16" /><path d="M17 4v16" /></svg>
);

interface SidebarProps {
  chats: string[];
  onNewChat: () => void;
}

export default function Sidebar({ chats, onNewChat }: SidebarProps) {
  return (
    <aside className="fixed left-0 top-0 h-screen w-[260px] bg-[#171717] text-[#ECECEC] flex flex-col font-sans shadow-lg z-40">
      {/* Top Navigation */}
      <nav className="flex flex-col gap-1 p-3 pb-2">
        <button onClick={onNewChat} className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-[#2F2F2F] transition-colors text-left">
          <EditIcon className="h-5 w-5" />
          <span className="text-base">New chat</span>
        </button>
        <button className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-[#2F2F2F] transition-colors text-left">
          <SearchIcon className="h-5 w-5" />
          <span className="text-base">Search chats</span>
        </button>
        <button className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-[#2F2F2F] transition-colors text-left">
          <LibraryIcon className="h-5 w-5" />
          <span className="text-base">Library</span>
        </button>
      </nav>

      {/* Your Chats Scrollable List */}
      <div className="flex-1 overflow-y-auto px-3 mt-3 pb-24 relative">
        {chats.length > 0 && <div className="font-semibold mb-2 text-xs text-[#888] px-2">Recent</div>}
        <div className="flex flex-col gap-1">
          {chats.map((chat, idx) => (
            <button key={idx} className="w-full text-left px-3 py-2 rounded-lg hover:bg-[#2F2F2F] transition-colors text-sm truncate">
              {chat}
            </button>
          ))}
        </div>
        {/* Fade mask at bottom */}
        <div className="pointer-events-none absolute bottom-0 left-0 w-full h-8 bg-gradient-to-t from-[#171717] to-transparent" />
      </div>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 w-full px-4 py-3 flex items-center gap-3 bg-[#171717] border-t border-[#222]">
        <div className="flex items-center justify-center h-9 w-9 rounded-full bg-[#2F2F2F] text-lg font-bold">IM</div>
        <div className="flex flex-col">
          <span className="font-semibold">Ibrahim Mahidpur</span>
          <span className="text-xs text-[#aaa]">Plus/Team</span>
        </div>
      </div>
    </aside>
  );
}
