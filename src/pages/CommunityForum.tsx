
import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ThemeToggle } from '../components/ThemeToggle';
import {
  MessageSquare, Heart, Share2, Search, Plus,
  TrendingUp, Users, Hash, MoreHorizontal, ArrowLeft,
  X
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

// Types
interface Author {
  name: string;
  avatar: string;
  role: string;
}

interface Comment {
  id: string;
  author: string;
  content: string;
  date: string;
  likes: number;
}

interface Post {
  id: string;
  title: string;
  content: string;
  author: Author;
  date: string;
  likes: number;
  views: number;
  comments: Comment[];
  tags: string[];
  category: string;
}

// ---- Components ----

// 1. Spotlight Effect Card
const SpotlightCard = ({ children, className = "" }: { children: React.ReactNode, className?: string }) => {
  const divRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [opacity, setOpacity] = useState(0);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!divRef.current) return;
    const rect = divRef.current.getBoundingClientRect();
    setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  };

  const handleFocus = () => {
    setOpacity(1);
  };

  const handleBlur = () => {
    setOpacity(0);
  };

  const handleMouseEnter = () => {
    setOpacity(1);
  };

  const handleMouseLeave = () => {
    setOpacity(0);
  };

  return (
    <div
      ref={divRef}
      onMouseMove={handleMouseMove}
      onFocus={handleFocus}
      onBlur={handleBlur}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className={`relative overflow-hidden rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 shadow-lg dark:backdrop-blur-md transition-colors ${className}`}
    >
      <div
        className="pointer-events-none absolute -inset-px opacity-0 transition duration-300"
        style={{
          opacity,
          background: `radial-gradient(600px circle at ${position.x}px ${position.y}px, rgba(120, 119, 198, 0.1), transparent 40%)`,
        }}
      />
      {children}
    </div>
  );
};

// 2. Animated Modal
const CreatePostModal = ({ isOpen, onClose, onSubmit }: { isOpen: boolean, onClose: () => void, onSubmit: (data: any) => void }) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [tagInput, setTagInput] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [category, setCategory] = useState('General');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ title, content, tags, category });
    setTitle('');
    setContent('');
    setTags([]);
    onClose();
  };

  const addTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-lg bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-white/10 rounded-2xl shadow-2xl overflow-hidden"
      >
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-white/5">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Create New Post</h2>
          <button onClick={onClose} className="p-2 text-gray-400 hover:text-white rounded-full hover:bg-white/10">
            <X size={20} />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-2 bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:border-purple-500"
              placeholder="What's on your mind?"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-4 py-2 bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:border-purple-500"
            >
              <option value="General">General</option>
              <option value="Health">Health</option>
              <option value="Remedies">Remedies</option>
              <option value="Support">Support</option>
              <option value="Experience">Experience</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Content</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="w-full px-4 py-3 bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:border-purple-500 min-h-[120px]"
              placeholder="Share your thoughts..."
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Tags</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                className="flex-1 px-4 py-2 bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:border-purple-500"
                placeholder="Add a tag..."
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
              />
              <button
                type="button"
                onClick={addTag}
                className="px-4 py-2 bg-gray-200 dark:bg-white/10 text-gray-900 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-white/20"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {tags.map(tag => (
                <span key={tag} className="px-2 py-1 text-xs bg-purple-500/20 text-purple-300 rounded-full flex items-center gap-1">
                  #{tag}
                  <button onClick={() => setTags(tags.filter(t => t !== tag))} className="hover:text-white"><X size={12} /></button>
                </span>
              ))}
            </div>
          </div>
          <div className="pt-4 flex justify-end gap-3">
            <button type="button" onClick={onClose} className="px-5 py-2 text-gray-400 hover:text-white">Cancel</button>
            <button type="submit" className="px-6 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-medium hover:shadow-lg hover:shadow-gray-500/25 transition-all">
              Post
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

// ---- Main Page ----

export default function CommunityForum() {
  const navigate = useNavigate();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Fetch posts
  const fetchPosts = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/forum/posts');
      const data = await response.json();
      if (data.success) {
        setPosts(data.posts);
      }
    } catch (error) {
      console.error('Failed to fetch posts:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPosts();
  }, []);

  const handleCreatePost = async (postData: any) => {
    try {
      const response = await fetch('http://localhost:5000/api/forum/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...postData, authorName: 'You' })
      });
      const data = await response.json();
      if (data.success) {
        fetchPosts(); // Reload posts
      }
    } catch (error) {
      console.error('Failed to create post:', error);
    }
  };

  const handleLike = async (id: string) => {
    try {
      await fetch(`http://localhost:5000/api/forum/posts/${id}/like`, { method: 'POST' });
      // Optimistic update
      setPosts(posts.map(p => p.id === id ? { ...p, likes: p.likes + 1 } : p));
    } catch (error) {
      console.error('Error liking post:', error);
    }
  };

  const filteredPosts = posts.filter(post => {
    const matchesFilter = filter === 'All' || post.category === filter;
    const matchesSearch = post.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      post.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      post.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesFilter && matchesSearch;
  });

  const categories = ['All', 'General', 'Health', 'Remedies', 'Support', 'Experience', 'Alternative Medicine'];

  return (
    <div className="min-h-screen w-full bg-[#f9fafb] dark:bg-[#050505] text-gray-900 dark:text-white font-sans selection:bg-purple-500/30 transition-colors duration-300">
      {/* Background Gradients */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-900/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-900/10 rounded-full blur-[120px]" />
      </div>

      {/* Content Container */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-8 flex flex-col md:flex-row gap-8">

        {/* Left Sidebar - Navigation/Categories */}
        <aside className="hidden md:block w-64 shrink-0 space-y-8 sticky top-8 h-fit">
          <div className="flex items-center gap-3 mb-8 cursor-pointer group" onClick={() => navigate('/')}>
            <div className="p-2 rounded-lg bg-white dark:bg-white/5 group-hover:bg-gray-50 dark:group-hover:bg-white/10 transition-colors border border-gray-200 dark:border-white/5 shadow-sm dark:shadow-none">
              <ArrowLeft size={20} className="text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
            </div>
            <span className="font-semibold text-gray-600 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-white tracking-wide">Back to Home</span>
          </div>

          <div className="space-y-4">
            <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider px-2">Feeds</h3>
            <nav className="space-y-1">
              <button className="w-full flex items-center gap-3 px-3 py-2 text-left rounded-lg bg-gray-200 dark:bg-white/10 text-gray-900 dark:text-white font-medium">
                <Hash size={18} />
                <span>Feed</span>
              </button>
              <button className="w-full flex items-center gap-3 px-3 py-2 text-left rounded-lg text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-white/5 transition-colors">
                <TrendingUp size={18} />
                <span>Popular</span>
              </button>
              <button className="w-full flex items-center gap-3 px-3 py-2 text-left rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-colors">
                <Users size={18} />
                <span>Following</span>
              </button>
            </nav>
          </div>

          <div className="space-y-4 pt-4 border-t border-white/5">
            <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider px-2">Topics</h3>
            <nav className="space-y-1">
              {categories.slice(1).map(cat => (
                <button
                  key={cat}
                  onClick={() => setFilter(cat)}
                  className={`w-full flex items-center gap-2 px-3 py-2 text-left rounded-lg text-sm transition-colors ${filter === cat ? 'text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-500/10' : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-white/5'}`}
                >
                  <div className={`w-1.5 h-1.5 rounded-full ${filter === cat ? 'bg-purple-500' : 'bg-gray-600'}`} />
                  {cat}
                </button>
              ))}
            </nav>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 min-w-0">
          {/* Header */}
          <header className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl md:text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400 transition-colors">
                Community Forum
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-2">Connect, share, and heal together.</p>
            </div>
            <div className="flex items-center gap-4">
              <ThemeToggle />
              <button
                onClick={() => setIsModalOpen(true)}
                className="flex items-center gap-2 px-6 py-3 bg-gray-900 dark:bg-white text-white dark:text-black rounded-xl font-bold hover:scale-105 transition-transform shadow-lg shadow-gray-500/10 dark:shadow-white/10"
              >
                <Plus size={20} />
                New Post
              </button>
            </div>
          </header>

          {/* Filter/Search Bar Mobile */}
          <div className="sticky top-0 z-40 bg-[#f9fafb]/80 dark:bg-[#050505]/80 backdrop-blur-xl py-4 mb-6 space-y-4 border-b border-gray-200 dark:border-white/5">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
              <input
                type="text"
                placeholder="Search discussions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl py-3 pl-11 pr-4 text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 focus:bg-gray-50 dark:focus:bg-white/10 transition-all"
              />
            </div>

            {/* Mobile Category Filter */}
            <div className="md:hidden flex gap-2 overflow-x-auto pb-2 no-scrollbar">
              {categories.map(cat => (
                <button
                  key={cat}
                  onClick={() => setFilter(cat)}
                  className={`px-4 py-1.5 rounded-full text-sm whitespace-nowrap border transition-colors ${filter === cat
                    ? 'bg-purple-600 border-purple-600 text-white'
                    : 'bg-transparent border-white/20 text-gray-300'
                    }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          {/* Posts Grid */}
          {loading ? (
            <div className="flex flex-col gap-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-48 rounded-xl bg-gray-200 dark:bg-white/5 animate-pulse" />
              ))}
            </div>
          ) : (
            <div className="grid gap-6">
              <AnimatePresence>
                {filteredPosts.map((post) => (
                  <motion.div
                    key={post.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{ duration: 0.3 }}
                  >
                    <SpotlightCard className="p-6 transition-all hover:border-purple-500/30 group bg-white dark:bg-white/5 border-gray-200 dark:border-white/10">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-center gap-3">
                          <img
                            src={post.author.avatar}
                            alt={post.author.name}
                            className="w-10 h-10 rounded-full bg-gray-800"
                          />
                          <div>
                            <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-300 transition-colors">
                              {post.author.name}
                            </h3>
                            <div className="flex items-center gap-2 text-xs text-gray-500">
                              <span className="px-1.5 py-0.5 rounded bg-white/10 text-gray-300">{post.author.role}</span>
                              <span>•</span>
                              <span>{new Date(post.date).toLocaleDateString()}</span>
                            </div>
                          </div>
                        </div>
                        <button className="p-2 text-gray-500 hover:text-white rounded-full hover:bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity">
                          <MoreHorizontal size={20} />
                        </button>
                      </div>

                      <div className="mt-4">
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">{post.title}</h2>
                        <p className="text-gray-600 dark:text-gray-400 leading-relaxed line-clamp-3">{post.content}</p>
                      </div>

                      {post.tags.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-4">
                          {post.tags.map(tag => (
                            <span key={tag} className="text-xs px-2 py-1 rounded-full bg-blue-500/10 text-blue-300 border border-blue-500/20">
                              #{tag}
                            </span>
                          ))}
                          <span className="text-xs px-2 py-1 rounded-full bg-white/5 text-gray-400 border border-white/10">
                            {post.category}
                          </span>
                        </div>
                      )}

                      <div className="flex items-center gap-6 mt-6 pt-6 border-t border-gray-200 dark:border-white/5">
                        <button
                          onClick={() => handleLike(post.id)}
                          className="flex items-center gap-2 text-gray-500 dark:text-gray-400 hover:text-pink-500 transition-colors group/like"
                        >
                          <Heart size={18} className="group-hover/like:fill-pink-500 transition-colors" />
                          <span className="text-sm font-medium">{post.likes}</span>
                        </button>
                        <button className="flex items-center gap-2 text-gray-500 dark:text-gray-400 hover:text-blue-400 transition-colors">
                          <MessageSquare size={18} />
                          <span className="text-sm font-medium">{post.comments.length}</span>
                        </button>
                        <button className="flex items-center gap-2 text-gray-500 dark:text-gray-400 hover:text-green-400 transition-colors">
                          <Share2 size={18} />
                          <span className="text-sm font-medium">Share</span>
                        </button>
                        <div className="ml-auto text-xs text-gray-600 flex items-center gap-1">
                          <TrendingUp size={14} />
                          {post.views} views
                        </div>
                      </div>
                    </SpotlightCard>
                  </motion.div>
                ))}
              </AnimatePresence>

              {filteredPosts.length === 0 && (
                <div className="text-center py-20 text-gray-500">
                  <p className="text-lg">No discussions found matching your search.</p>
                </div>
              )}
            </div>
          )}
        </main>

        {/* Right Sidebar - Stats/Trending */}
        <aside className="hidden lg:block w-80 shrink-0 space-y-6 sticky top-8 h-fit">
          <SpotlightCard className="p-5 bg-white dark:bg-white/5 border-gray-200 dark:border-white/10">
            <h3 className="font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <TrendingUp size={18} className="text-green-500 dark:text-green-400" />
              Trending Tags
            </h3>
            <div className="flex flex-wrap gap-2">
              {['#MentalHealth', '#Wellness', '#Ayurveda', '#Tips', '#Doctors'].map(tag => (
                <span key={tag} className="px-3 py-1 bg-gray-100 dark:bg-white/5 hover:bg-gray-200 dark:hover:bg-white/10 text-gray-700 dark:text-gray-300 text-sm rounded-lg cursor-pointer transition-colors border border-gray-200 dark:border-white/5 hover:border-gray-300 dark:hover:border-white/20">
                  {tag}
                </span>
              ))}
            </div>
          </SpotlightCard>

          <SpotlightCard className="p-5 bg-white dark:bg-white/5 border-gray-200 dark:border-white/10">
            <h3 className="font-bold text-gray-900 dark:text-white mb-4">Community Guidelines</h3>
            <ul className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex gap-2">
                <span className="text-green-400">•</span>
                Be respectful and kind to others
              </li>
              <li className="flex gap-2">
                <span className="text-green-400">•</span>
                No medical advice (consult doctors)
              </li>
              <li className="flex gap-2">
                <span className="text-green-400">•</span>
                Keep discussions on-topic
              </li>
            </ul>
          </SpotlightCard>
        </aside>
      </div>

      {/* Create Post Modal */}
      <AnimatePresence>
        {isModalOpen && (
          <CreatePostModal
            isOpen={isModalOpen}
            onClose={() => setIsModalOpen(false)}
            onSubmit={handleCreatePost}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
