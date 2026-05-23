
import express from 'express';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const router = express.Router();
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DATA_DIR = path.join(__dirname, 'forum-data');
const POSTS_FILE = path.join(DATA_DIR, 'posts.json');

// Ensure data directory exists
async function ensureDataDir() {
  try {
    await fs.access(DATA_DIR);
  } catch {
    await fs.mkdir(DATA_DIR, { recursive: true });
  }
}

// Ensure posts file exists with seed data
async function ensurePostsFile() {
  await ensureDataDir();
  try {
    await fs.access(POSTS_FILE);
  } catch {
    const seedData = [
      {
        id: '1',
        title: 'Best remedies for common cold?',
        content: 'I have been feeling under the weather lately. Does anyone have good home remedies?',
        author: { name: 'Sarah J.', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah', role: 'Member' },
        date: new Date().toISOString(),
        likes: 12,
        views: 342,
        comments: [
          { id: 'c1', author: 'Dr. Smith', content: 'Stay hydrated and get plenty of rest.', date: new Date().toISOString(), likes: 5 }
        ],
        tags: ['Health', 'Remedies'],
        category: 'General Health'
      },
      {
        id: '2',
        title: 'Ayurveda vs Modern Medicine',
        content: 'I am curious about the communitys thoughts on integrating Ayurveda with modern treatments.',
        author: { name: 'Raj Kumar', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Raj', role: 'Moderator' },
        date: new Date(Date.now() - 86400000).toISOString(),
        likes: 45,
        views: 1205,
        comments: [],
        tags: ['Ayurveda', 'Discussion'],
        category: 'Alternative Medicine'
      },
      {
        id: '3',
        title: 'Review of Local Pharmacies in Delhi',
        content: 'Sharing my experience with 24x7 pharmacies in South Delhi. Very helpful service!',
        author: { name: 'Priya M.', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Priya', role: 'Member' },
        date: new Date(Date.now() - 172800000).toISOString(),
        likes: 28,
        views: 560,
        comments: [],
        tags: ['Reviews', 'Delhi'],
        category: 'Local Resources'
      }
    ];
    await fs.writeFile(POSTS_FILE, JSON.stringify(seedData, null, 2));
  }
}

// Helper to load posts
async function loadPosts() {
  await ensurePostsFile();
  const data = await fs.readFile(POSTS_FILE, 'utf8');
  return JSON.parse(data);
}

// Helper to save posts
async function savePosts(posts) {
  await ensurePostsFile();
  await fs.writeFile(POSTS_FILE, JSON.stringify(posts, null, 2));
}

// GET /api/forum/posts - Get all posts
router.get('/posts', async (req, res) => {
  try {
    const posts = await loadPosts();
    res.json({ success: true, posts });
  } catch (error) {
    console.error('Error fetching posts:', error);
    res.status(500).json({ success: false, error: 'Failed to fetch posts' });
  }
});

// POST /api/forum/posts - Create new post
router.post('/posts', async (req, res) => {
  try {
    const { title, content, tags, category, authorName } = req.body;
    const posts = await loadPosts();

    const newPost = {
      id: Date.now().toString(),
      title,
      content,
      author: {
        name: authorName || 'Anonymous',
        avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${authorName || 'User'}`,
        role: 'Member'
      },
      date: new Date().toISOString(),
      likes: 0,
      views: 0,
      comments: [],
      tags: tags || [],
      category: category || 'General'
    };

    posts.unshift(newPost);
    await savePosts(posts);

    res.json({ success: true, post: newPost });
  } catch (error) {
    console.error('Error creating post:', error);
    res.status(500).json({ success: false, error: 'Failed to create post' });
  }
});

// POST /api/forum/posts/:id/like - Like a post
router.post('/posts/:id/like', async (req, res) => {
  try {
    const { id } = req.params;
    const posts = await loadPosts();
    const post = posts.find(p => p.id === id);

    if (post) {
      post.likes += 1;
      await savePosts(posts);
      res.json({ success: true, likes: post.likes });
    } else {
      res.status(404).json({ success: false, error: 'Post not found' });
    }
  } catch (error) {
    res.status(500).json({ success: false, error: 'Failed to like post' });
  }
});

export default router;
