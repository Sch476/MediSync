import { useState } from "react";
import { Link } from "react-router-dom";
import "./BlogHome.css";

const featured = {
  id: "featured",
  title: "How AI Middleware Is Cutting Insurance Claim Turnaround From Weeks to Days",
  category: "Product",
  categoryClass: "cat-product",
  excerpt:
    "Behind the scenes of MediSync's claims engine: how automated policy matching, document extraction, and fraud signals compress a process that used to take 21 days into a 48-hour cycle — without removing the human in the loop.",
  author: "Dr. Anaya Rao",
  date: "July 21, 2026",
  readTime: "8 min read",
  emoji: "⚙️",
};

const posts = [
  {
    id: "p1",
    title: "Understanding Your Health Policy: 7 Terms Every Patient Should Know",
    category: "Insurance",
    categoryClass: "cat-insurance",
    excerpt:
      "Copay, deductible, sub-limits, waiting periods — we break down the jargon on your policy document so you know exactly what you are covered for before you need it.",
    author: "Meera Nair",
    date: "July 18, 2026",
    readTime: "6 min read",
    emoji: "🛡️",
  },
  {
    id: "p2",
    title: "Preventive Care Checklist: What to Screen for in Your 30s, 40s and 50s",
    category: "Health",
    categoryClass: "cat-health",
    excerpt:
      "A decade-by-decade guide to the screenings that catch problems early, from blood pressure and lipid panels to cancer screenings — and how to schedule them.",
    author: "Dr. Sanjay Iyer",
    date: "July 15, 2026",
    readTime: "5 min read",
    emoji: "🩺",
  },
  {
    id: "p3",
    title: "Cashless vs. Reimbursement Claims: Which One Should You Choose?",
    category: "Insurance",
    categoryClass: "cat-insurance",
    excerpt:
      "The pros and cons of cashless hospital admission against pay-and-claim reimbursement, and the paperwork that trips most people up in each path.",
    author: "Rohan Desai",
    date: "July 12, 2026",
    readTime: "7 min read",
    emoji: "💳",
  },
  {
    id: "p4",
    title: "Reading a Hospital Bill Line by Line With the MediSync Bill Decoder",
    category: "Product",
    categoryClass: "cat-product",
    excerpt:
      "Consumables, procedure codes, room rent capping — we walk through a real discharge bill and show how the Bill Decoder flags the charges worth questioning.",
    author: "Priya Venkatesh",
    date: "July 9, 2026",
    readTime: "9 min read",
    emoji: "🧾",
  },
  {
    id: "p5",
    title: "Managing Diabetes: How Daily Health Check-Ins Improve Outcomes",
    category: "Health",
    categoryClass: "cat-health",
    excerpt:
      "Consistent self-monitoring is one of the strongest predictors of stable blood sugar. Here is how a 60-second daily check-in habit compounds over a year.",
    author: "Dr. Kavya Menon",
    date: "July 5, 2026",
    readTime: "4 min read",
    emoji: "📈",
  },
  {
    id: "p6",
    title: "New Data-Sharing Rules for Health Records: What Providers Need to Know",
    category: "Policy",
    categoryClass: "cat-policy",
    excerpt:
      "Recent changes to consent and interoperability requirements affect how hospitals, insurers and patients exchange records. A practical compliance summary.",
    author: "Arjun Kapoor",
    date: "July 1, 2026",
    readTime: "10 min read",
    emoji: "📋",
  },
];

const categories = [
  { name: "Health", count: 24 },
  { name: "Insurance", count: 18 },
  { name: "Product", count: 12 },
  { name: "Policy", count: 9 },
];

function PostMeta({ author, date, readTime }) {
  return (
    <div className="blog-meta">
      <strong>{author}</strong>
      <span className="blog-meta-dot" aria-hidden="true" />
      <span>{date}</span>
      <span className="blog-meta-dot" aria-hidden="true" />
      <span>{readTime}</span>
    </div>
  );
}

export default function BlogHome() {
  const [email, setEmail] = useState("");
  const [subscribed, setSubscribed] = useState(false);

  const handleSubscribe = (e) => {
    e.preventDefault();
    if (!email.trim()) return;
    setSubscribed(true);
    setEmail("");
  };

  return (
    <div className="blog-page">
      <header className="blog-nav">
        <div className="blog-wordmark">
          <span aria-hidden="true">⚕</span> MediSync <span>Blog</span>
        </div>
        <nav className="blog-nav-links" aria-label="Blog categories">
          <a className="blog-nav-link" href="#category-health">Health</a>
          <a className="blog-nav-link" href="#category-insurance">Insurance</a>
          <a className="blog-nav-link" href="#category-product">Product</a>
          <Link className="blog-nav-cta" to="/login">Sign In</Link>
        </nav>
      </header>

      <main className="blog-main">
        <article className="blog-featured" aria-labelledby="featured-title">
          <div className="blog-featured-media" aria-hidden="true">{featured.emoji}</div>
          <div className="blog-featured-body">
            <span className={`blog-tag ${featured.categoryClass}`}>{featured.category}</span>
            <h2 id="featured-title">{featured.title}</h2>
            <p className="blog-featured-excerpt">{featured.excerpt}</p>
            <PostMeta author={featured.author} date={featured.date} readTime={featured.readTime} />
          </div>
        </article>

        <div className="blog-content-grid">
          <section aria-labelledby="recent-title">
            <div className="blog-section-head">
              <h2 id="recent-title">Recent Articles</h2>
              <a href="#recent-title">View all</a>
            </div>

            <div className="blog-post-grid">
              {posts.map((post) => (
                <article className="blog-card" key={post.id}>
                  <div className="blog-card-media" aria-hidden="true">{post.emoji}</div>
                  <div className="blog-card-body">
                    <span className={`blog-tag ${post.categoryClass}`}>{post.category}</span>
                    <h3>{post.title}</h3>
                    <p className="blog-card-excerpt">{post.excerpt}</p>
                    <PostMeta author={post.author} date={post.date} readTime={post.readTime} />
                  </div>
                </article>
              ))}
            </div>
          </section>

          <aside className="blog-sidebar" aria-label="Blog sidebar">
            <div className="blog-widget">
              <h3>Categories</h3>
              <ul className="blog-cat-list">
                {categories.map((cat) => (
                  <li key={cat.name}>
                    <a href={`#category-${cat.name.toLowerCase()}`}>
                      {cat.name}
                      <span className="blog-cat-count">{cat.count}</span>
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div className="blog-widget blog-newsletter">
              <h3>Stay in the loop</h3>
              <p>
                Get the latest on health, insurance and MediSync product updates
                delivered to your inbox every week.
              </p>
              <form className="blog-newsletter-form" onSubmit={handleSubscribe}>
                <label htmlFor="blog-newsletter-email">Email address</label>
                <input
                  id="blog-newsletter-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                />
                <button type="submit">Subscribe</button>
                {subscribed && (
                  <p className="blog-newsletter-success" role="status">
                    Thanks for subscribing! Check your inbox to confirm.
                  </p>
                )}
              </form>
            </div>
          </aside>
        </div>
      </main>

      <footer className="blog-footer">
        <div className="blog-footer-inner">
          <div>
            <div className="blog-footer-brand">⚕ MediSync <span>Blog</span></div>
            <p>
              Insights on healthcare, insurance and the technology connecting
              patients, providers and insurers.
            </p>
          </div>
          <div className="blog-footer-cols">
            <div className="blog-footer-col">
              <h4>Topics</h4>
              <a href="#category-health">Health</a>
              <a href="#category-insurance">Insurance</a>
              <a href="#category-product">Product</a>
              <a href="#category-policy">Policy</a>
            </div>
            <div className="blog-footer-col">
              <h4>Company</h4>
              <Link to="/login">Sign In</Link>
              <a href="#about">About</a>
              <a href="#contact">Contact</a>
              <a href="#privacy">Privacy</a>
            </div>
          </div>
        </div>
        <div className="blog-footer-bottom">
          © 2026 MediSync. AI-Powered Healthcare Middleware. All rights reserved.
        </div>
      </footer>
    </div>
  );
}
