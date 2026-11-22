import { useState } from "react";

const isValidEmail = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
const isStrongPwd   = (v) => /^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$/.test(v);

export default function Register({ setPage }) {
  const [username, setUsername]               = useState("");
  const [email, setEmail]                     = useState("");
  const [password, setPassword]               = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword]       = useState(false);
  const [error, setError]                     = useState("");

  const handleRegister = () => {
    if (!username.trim())             return setError("Username is required.");
    if (!isValidEmail(email))         return setError("Enter a valid email address.");
    if (!isStrongPwd(password))       return setError("Password needs 8+ chars, a letter, a number, and a special character.");
    if (password !== confirmPassword) return setError("Passwords do not match.");
    setError("");
    setPage("login");
  };

  const handleKey = (e) => { if (e.key === "Enter") handleRegister(); };

  return (
    <div className="login-page">
      <div className="login-left">
        <div className="login-left-content">
          <div className="login-left-brand">FLIXNEST</div>
          <h2>Join the community</h2>
          <p>Create your free account and start discovering movies tailored to your taste across 7 languages and 1000+ titles.</p>
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

      <div className="login-right">
        <div className="login-form-wrap">
          <div className="login-form-header">
            <h1>Create account</h1>
            <p>Fill in the details below to get started for free.</p>
          </div>

          <div className="form-field">
            <label htmlFor="reg-username">Username</label>
            <input id="reg-username" type="text" placeholder="Choose a username"
              value={username} onChange={(e) => setUsername(e.target.value)} onKeyDown={handleKey} />
          </div>

          <div className="form-field">
            <label htmlFor="reg-email">Email address</label>
            <input id="reg-email" type="email" placeholder="you@example.com"
              value={email} onChange={(e) => setEmail(e.target.value)} onKeyDown={handleKey} />
          </div>

          <div className="form-field">
            <label htmlFor="reg-password">Password</label>
            <div className="input-group">
              <input id="reg-password" type={showPassword ? "text" : "password"}
                placeholder="Create a strong password"
                value={password} onChange={(e) => setPassword(e.target.value)} onKeyDown={handleKey} />
              <button type="button" className="toggle-password"
                onClick={() => setShowPassword((p) => !p)}
                aria-label={showPassword ? "Hide password" : "Show password"}>
                {showPassword ? "🙈" : "👁"}
              </button>
            </div>
          </div>

          <div className="form-field">
            <label htmlFor="reg-confirm">Confirm password</label>
            <input id="reg-confirm" type="password" placeholder="Repeat your password"
              value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} onKeyDown={handleKey} />
          </div>

          {error && <div className="error-message">⚠ {error}</div>}

          <button className="login-btn" onClick={handleRegister}>Create Account →</button>

          <p className="login-footer">
            Already have an account?{" "}
            <a href="#" onClick={(e) => { e.preventDefault(); setPage("login"); }}>Sign in</a>
          </p>
        </div>
      </div>
    </div>
  );
}
