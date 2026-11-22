import { useState, useEffect } from "react";
import API from "../services/api";
import "../styles/MovieDetails.css";

const PLACEHOLDER = "https://placehold.co/400x600/0c0f1a/444?text=No+Poster";

function InfoBadge({ label, value }) {
  if (!value) return null;
  return (
    <div className="md-badge">
      <span className="md-badge-label">{label}</span>
      <span className="md-badge-value">{value}</span>
    </div>
  );
}

export default function MovieDetails({ movie, user, onBack, setPage, setUser, setSelectedMovie }) {
  const [imgErr, setImgErr] = useState(false);
  const [similar, setSimilar] = useState([]);

  useEffect(() => {
    setSimilar([]);
    setImgErr(false);
    API.get("/recommend", { params: { movie_name: movie.movie_name } })
      .then(res => setSimilar(res.data.movies || []))
      .catch(() => setSimilar([]));
  }, [movie.movie_name]);

  const genres  = movie.genre  ? movie.genre.split(",").map(g => g.trim()).filter(Boolean)  : [];
  const actors  = movie.actor  ? movie.actor.split(",").map(a => a.trim()).filter(Boolean)  : [];
  const keywords = movie.keywords ? movie.keywords.split(",").map(k => k.trim()).filter(Boolean) : [];
  const initials = (user || "M").charAt(0).toUpperCase();

  const ratingNum = parseFloat(movie.rating);
  const ratingPct = !isNaN(ratingNum) ? Math.round((ratingNum / 10) * 100) : null;

  return (
    <div className="md-page">

      {/* ── Topbar ── */}
      <header className="dashboard-topbar">
        <div className="topbar-brand">FLIXNEST</div>
        <div className="topbar-right">
          <div className="topbar-user">
            <div className="topbar-avatar">{initials}</div>
            <span>{user || "Movie Fan"}</span>
          </div>
          <button className="logout-btn" onClick={() => { setUser(""); setPage("home"); }}>
            Sign out
          </button>
        </div>
      </header>

      {/* ── Back button ── */}
      <div className="md-back-wrap">
        <button className="md-back-btn" onClick={onBack}>
          ← Back to results
        </button>
      </div>

      {/* ── Hero backdrop blur ── */}
      <div className="md-hero">
        {(movie.poster_url && !imgErr) && (
          <div className="md-backdrop"
            style={{ backgroundImage: `url(${movie.poster_url})` }} />
        )}
        <div className="md-backdrop-overlay" />

        <div className="md-hero-content">

          {/* Poster */}
          <div className="md-poster-wrap">
            <img
              className="md-poster"
              src={!imgErr && movie.poster_url ? movie.poster_url : PLACEHOLDER}
              alt={movie.movie_name}
              onError={() => setImgErr(true)}
            />
            {movie.rating && (
              <div className="md-rating-badge">
                <span className="md-rating-star">⭐</span>
                <span className="md-rating-num">{movie.rating}</span>
                <span className="md-rating-max">/10</span>
              </div>
            )}
          </div>

          {/* Info */}
          <div className="md-info">
            <div className="md-lang-year">
              {movie.language && <span className="md-lang">{movie.language}</span>}
              {movie.year     && <span className="md-year">{movie.year}</span>}
            </div>

            <h1 className="md-title">{movie.movie_name || "Untitled"}</h1>

            {/* Genre tags */}
            {genres.length > 0 && (
              <div className="md-genres">
                {genres.map(g => <span key={g} className="md-genre-tag">{g}</span>)}
              </div>
            )}

            <div className="md-hero-meta-grid">
              {movie.director && (
                <div className="md-hero-meta-item">
                  <span className="md-hero-meta-label">Director</span>
                  <span className="md-hero-meta-value">{movie.director}</span>
                </div>
              )}
              {actors.length > 0 && (
                <div className="md-hero-meta-item">
                  <span className="md-hero-meta-label">Cast</span>
                  <span className="md-hero-meta-value">{actors.join(", ")}</span>
                </div>
              )}
              {movie.rating && (
                <div className="md-hero-meta-item">
                  <span className="md-hero-meta-label">Rating</span>
                  <span className="md-hero-meta-value">⭐ {movie.rating} / 10</span>
                </div>
              )}
              {genres.length > 0 && (
                <div className="md-hero-meta-item">
                  <span className="md-hero-meta-label">Genre</span>
                  <span className="md-hero-meta-value">{genres.join(", ")}</span>
                </div>
              )}
            </div>

            {/* Rating bar */}
            {ratingPct !== null && (
              <div className="md-rating-bar-wrap">
                <div className="md-rating-bar">
                  <div className="md-rating-fill" style={{ width: `${ratingPct}%` }} />
                </div>
                <span className="md-rating-label">{movie.rating} / 10</span>
              </div>
            )}

            {/* Description */}
            {movie.description && (
              <p className="md-description">{movie.description}</p>
            )}

            {/* Key details grid */}
            <div className="md-badges">
              <InfoBadge label="Director"  value={movie.director} />
              <InfoBadge label="Language"  value={movie.language} />
              <InfoBadge label="Year"      value={movie.year} />
              <InfoBadge label="Rating"    value={movie.rating ? `${movie.rating} / 10` : null} />
            </div>


          </div>
        </div>
      </div>

      {/* ── Details section ── */}
      <div className="md-body">

        {/* Cast */}
        {actors.length > 0 && (
          <section className="md-section">
            <h2 className="md-section-title">Cast</h2>
            <div className="md-cast-list">
              {actors.map(a => (
                <div key={a} className="md-cast-card">
                  <div className="md-cast-avatar">
                    {a.charAt(0).toUpperCase()}
                  </div>
                  <span className="md-cast-name">{a}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Keywords */}
        {keywords.length > 0 && (
          <section className="md-section">
            <h2 className="md-section-title">Keywords</h2>
            <div className="md-keywords">
              {keywords.map(k => (
                <span key={k} className="md-keyword">{k}</span>
              ))}
            </div>
          </section>
        )}

        {/* Full details table */}
        <section className="md-section">
          <h2 className="md-section-title">Movie Details</h2>
          <div className="md-details-table">
            {[
              ["Title",    movie.movie_name],
              ["Language", movie.language],
              ["Year",     movie.year],
              ["Genre",    movie.genre],
              ["Director", movie.director],
              ["Cast",     movie.actor],
              ["Rating",   movie.rating ? `${movie.rating} / 10` : null],
              ["Keywords", movie.keywords],
            ].filter(([, v]) => v).map(([label, value]) => (
              <div key={label} className="md-detail-row">
                <span className="md-detail-label">{label}</span>
                <span className="md-detail-value">{value}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Similar Movies */}
        {similar.length > 0 && (
          <section className="md-section">
            <h2 className="md-section-title">Similar Movies</h2>
            <div className="md-similar-grid">
              {similar.map((m, i) => (
                <div key={i} className="md-similar-card"
                  onClick={() => setSelectedMovie && setSelectedMovie(m)}
                  role="button" tabIndex={0}
                  onKeyDown={(e) => e.key === "Enter" && setSelectedMovie && setSelectedMovie(m)}>
                  <img
                    src={m.poster_url || "https://placehold.co/150x220/0c0f1a/444?text=No+Poster"}
                    alt={m.movie_name}
                    onError={(e) => { e.target.src = "https://placehold.co/150x220/0c0f1a/444?text=No+Poster"; }}
                  />
                  <div className="md-similar-info">
                    <p className="md-similar-title">{m.movie_name}</p>
                    <p className="md-similar-meta">{m.year} {m.rating ? `⭐ ${m.rating}` : ""}</p>
                    <p className="md-similar-genre">{m.genre}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

      </div>
    </div>
  );
}
