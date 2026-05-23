# 💬 Feature 6: Community Health Forum

## Overview

The **Community Health Forum** is a full-featured social discussion platform built for health-focused community engagement. Users can create posts, interact via likes/comments, filter by categories, search topics, and browse trending content — all in a beautifully animated dark/light mode interface.

Posts are stored persistently in the backend and fetched on load, enabling a real community feel with backend-synced likes and post creation.

---

## 📁 Key Files

| File | Role |
|------|------|
| [`src/pages/CommunityForum.tsx`](../src/pages/CommunityForum.tsx) | Full forum page (524 lines) |
| [`src/components/ThemeToggle.tsx`](../src/components/ThemeToggle.tsx) | Dark/Light mode toggle |
| [`backend/forum-api.js`](../backend/forum-api.js) | Forum REST API (CRUD) |
| [`backend/forum-data/`](../backend/forum-data/) | JSON post persistence |

---

## 🧩 Features

### 1. Spotlight Card Effect
Cards have a premium mouse-tracking spotlight hover effect:

```tsx
const SpotlightCard = ({ children }) => {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [opacity, setOpacity] = useState(0);
  
  const handleMouseMove = (e) => {
    const rect = divRef.current.getBoundingClientRect();
    setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  };
  
  // Renders a radial gradient that follows the cursor
  return (
    <div onMouseMove={handleMouseMove}>
      <div style={{
        background: `radial-gradient(600px circle at ${position.x}px ${position.y}px, 
                     rgba(120,119,198,0.1), transparent 40%)`,
        opacity
      }} />
      {children}
    </div>
  );
};
```

### 2. Animated Post Creation Modal
Framer Motion powered modal with spring animation:

```tsx
<motion.div
  initial={{ opacity: 0, scale: 0.95 }}
  animate={{ opacity: 1, scale: 1 }}
  exit={{ opacity: 0, scale: 0.95 }}
>
  {/* Post form */}
</motion.div>
```

The modal includes:
- **Title field** (required)
- **Category selector**: General, Health, Remedies, Support, Experience
- **Content textarea** (required)
- **Tag system**: Add/remove hashtags dynamically with Enter key support

### 3. Category Filtering
7 post categories with real-time filtering:
- All, General, Health, Remedies, Support, Experience, Alternative Medicine

Desktop: Sidebar navigation with active state highlighting  
Mobile: Horizontal scrollable pills

### 4. Full-Text Search
Real-time search across title, content, and tags:

```typescript
const filteredPosts = posts.filter(post => {
  const matchesFilter = filter === 'All' || post.category === filter;
  const matchesSearch = 
    post.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    post.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
    post.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
  return matchesFilter && matchesSearch;
});
```

### 5. Optimistic Like System
Likes update instantly in the UI without waiting for the server:

```typescript
const handleLike = async (id: string) => {
  // Optimistic update — instant UI change
  setPosts(posts.map(p => p.id === id ? { ...p, likes: p.likes + 1 } : p));
  
  // Background sync with server
  await fetch(`http://localhost:5000/api/forum/posts/${id}/like`, { method: 'POST' });
};
```

### 6. Post Cards
Each post card displays:
- Author avatar, name, and role badge
- Post date
- Title and content (3-line clamp)
- Hashtag badges (blue) + category badge
- ❤️ Like count, 💬 Comment count, 📤 Share button
- 👁 View count
- Options menu (appears on hover)

### 7. Animated Feed
Posts animate in and out with Framer Motion's `AnimatePresence`:

```tsx
<AnimatePresence>
  {filteredPosts.map(post => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.3 }}
    >
      <SpotlightCard>...</SpotlightCard>
    </motion.div>
  ))}
</AnimatePresence>
```

### 8. Dark / Light Mode
Full theme toggle with smooth CSS transitions:
- `dark:bg-[#050505]` / `bg-[#f9fafb]`
- Ambient gradient orbs in background (purple + blue)
- All components adapt: borders, text, inputs, buttons

### 9. Right Sidebar (Desktop)
- **Trending Tags**: #MentalHealth, #Wellness, #Ayurveda, #Tips, #Doctors
- **Community Guidelines**: Safe space rules

### 10. Loading Skeleton
While posts load, animated pulse placeholders are shown:
```tsx
{[1, 2, 3].map(i => (
  <div key={i} className="h-48 rounded-xl bg-white/5 animate-pulse" />
))}
```

---

## 🔌 API Endpoints

Served from `backend/forum-api.js`:

### `GET /api/forum/posts`
Returns all posts sorted by date (newest first).

**Response:**
```json
{
  "success": true,
  "posts": [{
    "id": "post_001",
    "title": "Natural remedies for monsoon cold",
    "content": "Sharing what worked for me...",
    "author": {
      "name": "Priya Sharma",
      "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Priya",
      "role": "Community Member"
    },
    "date": "2025-06-01T10:00:00Z",
    "likes": 42,
    "views": 187,
    "comments": [...],
    "tags": ["cold", "remedies", "monsoon"],
    "category": "Remedies"
  }]
}
```

### `POST /api/forum/posts`
Create a new post.

**Request:**
```json
{
  "title": "My experience with yoga for anxiety",
  "content": "For the past 3 months...",
  "tags": ["yoga", "anxiety", "wellness"],
  "category": "Health",
  "authorName": "You"
}
```

### `POST /api/forum/posts/:id/like`
Increment the like count for a post.

**Response:**
```json
{ "success": true, "likes": 43 }
```

---

## 📦 Data Persistence

Posts are stored in `backend/forum-data/` as JSON files, loaded and saved by the API.

### Post Schema
```typescript
interface Post {
  id: string;
  title: string;
  content: string;
  author: {
    name: string;
    avatar: string;  // DiceBear avatar URL
    role: string;
  };
  date: string;      // ISO timestamp
  likes: number;
  views: number;
  comments: Comment[];
  tags: string[];
  category: string;
}
```

---

## 🏗️ Architecture

```
Frontend (CommunityForum.tsx)
    ├── On mount: fetchPosts() → GET /api/forum/posts
    ├── Create Post → POST /api/forum/posts → fetchPosts()
    ├── Like → Optimistic update → POST /api/forum/posts/:id/like
    └── Filter/Search → Client-side filtering of loaded posts

Backend (forum-api.js)
    ├── GET /api/forum/posts → Load from forum-data/*.json
    ├── POST /api/forum/posts → Append to JSON store
    └── POST /api/forum/posts/:id/like → Increment + save
```

---

## 📊 Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React + TypeScript |
| Animations | Framer Motion |
| Icons | Lucide React |
| Theme | CSS custom properties + Tailwind dark mode |
| Avatars | DiceBear API |
| Backend | Node.js + Express |
| Data | JSON flat file persistence |

---

## 🚀 Running

```bash
cd backend
npm start   # Forum API at port 5000

npm run dev # Frontend at port 5173
```

Navigate to: `http://localhost:5173/community`
