import { useState, useEffect } from "react";
import API from "../services/api";
import "../styles/MovieCard.css";

const PLACEHOLDER = "https://placehold.co/300x450/0c0f1a/444?text=No+Poster";

const LANGUAGES = ["Kannada", "Tamil", "Telugu", "Malayalam", "Hindi", "English", "Korean"];
const GENRES = ["Action", "Romance", "Thriller", "Comedy", "Drama"];
const MOODS = [
  { key: "happy", emoji: "😊", label: "Happy" },
  { key: "sad", emoji: "😢", label: "Sad" },
  { key: "excited", emoji: "🤩", label: "Excited" },
  { key: "romantic", emoji: "💘", label: "Romantic" },
  { key: "scary", emoji: "👻", label: "Scary" },
  { key: "nostalgic", emoji: "🕰️", label: "Nostalgic" },
  { key: "funny", emoji: "😂", label: "Funny" },
];

function SkeletonCard() {
  return (
    <div className="movie-card-skeleton">
      <div className="skeleton-poster" />
      <div className="skeleton-body">
        <div className="skeleton-line medium" />
        <div className="skeleton-line short" />
        <div className="skeleton-line medium" />
      </div>
    </div>
  );
}

function MovieCard({ movie, onClick }) {
  const [imgErr, setImgErr] = useState(false);
  const genres = movie.genre ? movie.genre.split(",").slice(0, 2) : [];

  return (
    <div className="movie-card" onClick={onClick} role="button" tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && onClick()}>
      <div className="movie-card-poster">
        <img
          src={!imgErr && movie.poster_url ? movie.poster_url : PLACEHOLDER}
          alt={movie.movie_name}
          onError={() => setImgErr(true)}
          loading="lazy"
        />
        {movie.language && <span className="movie-card-lang">{movie.language}</span>}
        {movie.rating   && <span className="movie-card-rating">⭐ {movie.rating}</span>}
        <div className="movie-card-hover-overlay">
          <span className="movie-card-view-btn">View Details</span>
        </div>
      </div>

      <div className="movie-card-body">
        <h3 className="movie-card-title">{movie.movie_name || "Untitled"}</h3>

        {genres.length > 0 && (
          <div className="movie-card-genres">
            {genres.map(g => <span key={g} className="genre-tag">{g.trim()}</span>)}
          </div>
        )}

        {movie.description && <p className="movie-card-desc">{movie.description}</p>}

        <div className="movie-card-meta">
          {movie.director && <p><strong>Dir:</strong> {movie.director}</p>}
          {movie.actor    && <p><strong>Cast:</strong> {movie.actor}</p>}
        </div>

        <div className="movie-card-footer">
          <span className="movie-card-year">{movie.year || ""}</span>
        </div>
      </div>
    </div>
  );
}

function SingleMovieSummary({ movie }) {
  const genres = movie.genre ? movie.genre.split(",").map((g) => g.trim()).filter(Boolean).slice(0, 3) : [];
  const actors = movie.actor ? movie.actor.split(",").map((a) => a.trim()).filter(Boolean).slice(0, 4) : [];

  return (
    <section className="single-movie-summary">
      <div className="sms-poster">
        <img
          src={movie.poster_url || PLACEHOLDER}
          alt={movie.movie_name}
          loading="lazy"
        />
      </div>
      <div className="sms-content">
        <h2>{movie.movie_name}</h2>
        <div className="sms-meta">
          {movie.director && <span><strong>Director:</strong> {movie.director}</span>}
          {movie.rating && <span><strong>Rating:</strong> ⭐ {movie.rating}</span>}
          {movie.year && <span><strong>Year:</strong> {movie.year}</span>}
        </div>
        {genres.length > 0 && (
          <div className="sms-genres">
            {genres.map((genre) => (
              <span key={genre}>{genre}</span>
            ))}
          </div>
        )}
        {actors.length > 0 && (
          <div className="sms-cast">
            <strong>Cast:</strong> {actors.join(", ")}
          </div>
        )}
        {movie.description && <p className="sms-description">{movie.description}</p>}
      </div>
    </section>
  );
}

export default function Dashboard({ user, setPage, setUser, setSelectedMovie }) {
  const [query, setQuery]     = useState("");
  const [results, setResults] = useState([]);
  const [status, setStatus]   = useState("idle");
  const [searched, setSearched] = useState("");
  useEffect(() => {
    const mood = localStorage.getItem('moodQuery');
    if (mood) {
      (async () => {
        setStatus('loading');
        try {
          const res = await API.get(`/mood/${encodeURIComponent(mood)}`);
          setResults(res.data.movies || []);
          setSearched(`${mood} (mood)`);
          setStatus('done');
        } catch (e) {
          setResults([]);
          setStatus('error');
        } finally {
          localStorage.removeItem('moodQuery');
        }
      })();
    }
  }, []);

  const doSearch = async (term) => {
    const q = term.trim();
    if (!q) return;
    setQuery(q);
    setStatus("loading");
    setSearched(q);
    try {
      const res = await API.get("/search", { params: { query: q } });
      setResults(res.data.movies || []);
      setStatus("done");
    } catch {
      setResults([]);
      setStatus("error");
    }
  };

  const doLanguageSearch = async (lang) => {
    setStatus("loading");
    setSearched(lang);
    try {
      const res = await API.get(`/language/${encodeURIComponent(lang)}`);
      let movies = res.data.movies || [];
      // If Korean, also fetch Chinese movies
      if (lang.toLowerCase() === "korean") {
        const chineseRes = await API.get(`/language/chinese`);
        const chineseMovies = chineseRes.data.movies || [];
        movies = [...movies, ...chineseMovies];
        setSearched("Korean & Chinese");
      }
      setResults(movies);
      setStatus("done");
    } catch {
      setResults([]);
      setStatus("error");
    }
  };

  const doGenreSearch = async (genre) => {
    setStatus("loading");
    setSearched(genre);
    try {
      const res = await API.get(`/genre/${encodeURIComponent(genre)}`);
      setResults(res.data.movies || []);
      setStatus("done");
    } catch {
      setResults([]);
      setStatus("error");
    }
  };

  const handleKey = (e) => { if (e.key === "Enter") doSearch(query); };
  const initials  = (user || "M").charAt(0).toUpperCase();

  return (
    <div className="dashboard-page">
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

      <section className="dashboard-hero">
        <h1>What do you want to watch?</h1>
        <p>Search by title, genre, actor, director, or language</p>
        <div className="search-panel">
          <input type="text" value={query}
            onChange={(e) => setQuery(e.target.value)} onKeyDown={handleKey}
            placeholder="e.g. Kantara, Action, Dhanush, Kannada…" autoFocus />
          <button className="search-btn" onClick={() => doSearch(query)} disabled={status === "loading"}>
            {status === "loading" ? "Searching…" : "Search"}
          </button>
        </div>

        {/* Row 1: Moods */}
        <div style={{ marginTop: 24 }}>
          <div className="filter-chips">
            {MOODS.map(m => (
              <button key={m.key} className="chip mood-chip" onClick={() => {
                setStatus('loading');
                (async () => {
                  try {
                    const res = await API.get(`/mood/${encodeURIComponent(m.key)}`);
                    setResults(res.data.movies || []);
                    setSearched(`${m.label} (mood)`);
                    setStatus('done');
                  } catch (e) {
                    setResults([]);
                    setStatus('error');
                  }
                })();
              }}>
                <span style={{ marginRight: 8 }}>{m.emoji}</span>{m.label}
              </button>
            ))}
          </div>
        </div>

        {/* Row 2: Languages */}
        <div style={{ marginTop: 24 }}>
          <div className="filter-chips">
            {LANGUAGES.map(lang => (
              <button key={lang} className="chip" onClick={() => doLanguageSearch(lang)}>{lang}</button>
            ))}
          </div>
        </div>

        {/* Row 3: Genres */}
        <div style={{ marginTop: 24 }}>
          <div className="filter-chips">
            {GENRES.map(genre => (
              <button key={genre} className="chip" onClick={() => doGenreSearch(genre)}>{genre}</button>
            ))}
          </div>
        </div>
      </section>

      <main className="dashboard-results">
        {status === "loading" && (
          <div className="movie-grid">
            {Array.from({ length: 10 }).map((_, i) => <SkeletonCard key={i} />)}
          </div>
        )}

        {status === "error" && (
          <div className="search-message">
            <div className="search-message-icon">⚠️</div>
            <p>Something went wrong. Please try again.</p>
          </div>
        )}

        {status === "done" && results.length === 0 && (
          <div className="search-message">
            <div className="search-message-icon">🎬</div>
            <p>No movies found for "<strong>{searched}</strong>". Try a different keyword.</p>
          </div>
        )}

        {status === "done" && results.length > 0 && (
          <>
            <div className="results-header">
              <p className="results-count">
                <strong>{results.length}</strong> result{results.length !== 1 ? "s" : ""} for "{searched}"
              </p>
            </div>
            {((results.length === 1)
              || results.find(movie => movie.movie_name?.toLowerCase() === searched.trim().toLowerCase())) && (
              <SingleMovieSummary
                movie={results.length === 1
                  ? results[0]
                  : results.find(movie => movie.movie_name?.toLowerCase() === searched.trim().toLowerCase())}
              />
            )}
            <div className="movie-grid">
              {results.map((movie, i) => (
                <MovieCard
                  key={`${movie.movie_name}-${i}`}
                  movie={movie}
                  onClick={() => setSelectedMovie(movie)}
                />
              ))}
            </div>
          </>
        )}

        {status === "idle" && (
          <div className="search-message">
            <div className="search-message-icon">🍿</div>
            <p>Search above or tap a quick filter to get started.</p>
          </div>
        )}
      </main>
    </div>
  );
}
