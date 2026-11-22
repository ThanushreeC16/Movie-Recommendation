import { useState } from "react";

export default function Login({ setPage, setUser }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = () => {
    if (!email || !password) return;
    setUser(email.split("@")[0] || "Movie Fan");
    setPage("dashboard");
  };

  const handleKey = (e) => { if (e.key === "Enter") handleLogin(); };

  return (
    <div className="login-page">

      {/* Left decorative panel */}
      <div className="login-left">
        <div className="login-left-content">
          <div className="login-left-brand">FLIXNEST</div>
          <h2>Your personal movie universe</h2>
          <p>Discover, search, and get smart recommendations across 1000+ movies in 7 languages.</p>
          <div className="login-left-features">
            {[
              ["🎬", "1000+ curated movies"],
              ["🌐", "7 languages supported"],
              ["⭐", "Movie Ratings"],
            ].map(([icon, text]) => (
              <div className="login-feature" key={text}>
                <div className="login-feature-icon">{icon}</div>
                <span>{text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right form panel */}
      <div className="login-right">
        <div className="login-form-wrap">
          <div className="login-form-header">
            <h1>Welcome back</h1>
            <p>Sign in to continue to your movie dashboard.</p>
          </div>

          <div className="form-field">
            <label htmlFor="email">Email address</label>
            <input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyDown={handleKey}
            />
          </div>

          <div className="form-field">
            <label htmlFor="password">Password</label>
            <div className="input-group">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={handleKey}
              />
              <button
                type="button"
                className="toggle-password"
                onClick={() => setShowPassword(p => !p)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? "🙈" : "👁"}
              </button>
            </div>
          </div>

          <button className="login-btn" onClick={handleLogin}>Sign In →</button>

          <p className="login-footer">
            Don't have an account?{" "}
            <a href="#" onClick={(e) => { e.preventDefault(); setPage("register"); }}>
              Create one
            </a>
          </p>
        </div>
      </div>

    </div>
  );
}
