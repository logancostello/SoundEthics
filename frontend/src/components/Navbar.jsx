function Navbar() {
  return (
    <nav style={{
      padding: '18px 32px',
      borderBottom: '1px solid var(--color-border)',
      background: 'var(--color-bg)',
    }}>
      <span style={{
        color: 'var(--color-text-label)',
        fontFamily: 'var(--font-heading)',
        fontSize: 'var(--font-size-heading)',
        letterSpacing: '0.06em',
      }}>
        Sound Ethics
      </span>
    </nav>
  )
}

export default Navbar