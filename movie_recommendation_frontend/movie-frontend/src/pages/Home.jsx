export default function Home({ setPage }) {
  return (
    <div className="home-page">
      <div className="home-overlay">

        {/* Navbar */}
        <nav className="navbar">
          <div className="brand-name">FLIXNEST</div>
          <div className="nav-buttons">
            <button className="login-btn" onClick={() => setPage("login")}>Sign In</button>
            <button className="register-btn" onClick={() => setPage("register")}>Register</button>
          </div>
        </nav>

        {/* Hero */}
        <div className="hero-content">
          <div className="hero-eyebrow">
            <span>🎬</span> Smart Movie Recommendations
          </div>

          <h1>
            Discover Your<br />
            <em>Next Favorite</em><br />
            Movie
          </h1>

          <p>
            Search 1000+ movies across Kannada, Tamil, Telugu, Malayalam,
            Hindi, English &amp; Korean — by title, genre, actor, or director.
          </p>

          <div className="hero-actions">
            <button className="explore-btn" onClick={() => setPage("login")}>
              Explore Movies →
            </button>
            <button className="hero-secondary-btn" onClick={() => setPage("register")}>
              Create Account
            </button>
          </div>

          <div className="hero-stats">
            <div className="stat-item">
              <div className="stat-number">1000<span>+</span></div>
              <div className="stat-label">Movies</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">7<span>+</span></div>
              <div className="stat-label">Languages</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">AI<span>✦</span></div>
              <div className="stat-label">Powered</div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
