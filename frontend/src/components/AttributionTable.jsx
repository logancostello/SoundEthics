/*
  AttributionTable
  props:
    - tracks: array of { name: string, stem: string }
  Shows even-split attribution percentages per source track, with stem used.
*/
export default function AttributionTable({ tracks }) {
  if (!tracks || tracks.length === 0) return null;

  const raw = 100 / tracks.length;
  const truncated = Math.floor(raw * 10) / 10;
  const percents = tracks.map(() => truncated);

  return (
    <div style={styles.wrapper}>
      <div style={styles.header}>
        <span style={styles.headerCell}>Source</span>
        <span style={styles.headerCell}>Stem</span>
        <span style={{ ...styles.headerCell, textAlign: "right" }}>Attribution</span>
      </div>

      {tracks.map((track, i) => (
        <div
          key={track.name}
          style={{
            ...styles.row,
            borderBottom: i < tracks.length - 1 ? "1px solid var(--icon-btn-border)" : "none",
          }}
        >
          {/* Source name */}
          <span style={styles.nameCell}>
            <span style={styles.dot} />
            {track.name}
          </span>

          {/* Stem — plain muted text with a leading slash for visual separation */}
          <span style={styles.stemCell}>
            {track.stem}
          </span>

          {/* Percentage + fill bar */}
          <span style={styles.pctCell}>
            <span style={styles.pctNumber}>{percents[i].toFixed(0)}%</span>
            <span style={styles.barTrack}>
              <span style={{ ...styles.barFill, width: `${percents[i]}%` }} />
            </span>
          </span>
        </div>
      ))}
    </div>
  );
}

const styles = {
  wrapper: {
    width: "100%",
    boxSizing: "border-box",
    border: "1px solid var(--icon-btn-border)",
    background: "var(--color-bg-panel)",
    marginTop: 10,
  },
  header: {
    display: "grid",
    gridTemplateColumns: "1fr 90px 140px",
    padding: "6px 14px",
    borderBottom: "1px solid var(--icon-btn-border)",
    background: "rgba(255,255,255,0.03)",
  },
  headerCell: {
    fontSize: "var(--font-size-xs)",
    color: "var(--color-text-muted)",
    textTransform: "uppercase",
    letterSpacing: "0.08em",
    fontFamily: "var(--font-primary)",
  },
  row: {
    display: "grid",
    gridTemplateColumns: "1fr 90px 140px",
    alignItems: "center",
    padding: "8px 14px",
  },
  nameCell: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    fontSize: "var(--font-size-small)",
    color: "var(--color-text)",
    fontFamily: "var(--font-primary)",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: "50%",
    background: "var(--color-accent)",
    flexShrink: 0,
  },
  stemCell: {
    display: "flex",
    alignItems: "center",
    gap: 4,
    fontSize: "var(--font-size-xs)",
    color: "var(--color-text-muted)",
    fontFamily: "var(--font-primary)",
    textTransform: "uppercase",
    letterSpacing: "0.06em",
  },
  pctCell: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    justifyContent: "flex-end",
  },
  pctNumber: {
    fontSize: "var(--font-size-small)",
    color: "var(--color-text)",
    fontFamily: "var(--font-primary)",
    minWidth: 36,
    textAlign: "right",
    flexShrink: 0,
  },
  barTrack: {
    flex: 1,
    height: 3,
    background: "var(--icon-btn-border)",
    position: "relative",
    overflow: "hidden",
    maxWidth: 70,
  },
  barFill: {
    position: "absolute",
    left: 0,
    top: 0,
    height: "100%",
    background: "var(--color-accent)",
    transition: "width 0.4s ease",
  },
};