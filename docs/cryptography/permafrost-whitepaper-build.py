#!/usr/bin/env python3
"""
PERMAFROST Whitepaper PDF Generator
Post-Quantum Threshold ML-DSA with Dealerless Key Generation
"""

import sys
sys.path.insert(0, '/root/openclaw/skills/pdf-generator')
import generator as g

# ──────────────────────────────────────────────────────────────────────────────
# Create document
# ──────────────────────────────────────────────────────────────────────────────
doc, story, cw = g.create_document('/tmp/permafrost-whitepaper.pdf')
S = g.get_styles()

# ──────────────────────────────────────────────────────────────────────────────
# Helper: safely wrap text for Paragraph (escape XML)
# ──────────────────────────────────────────────────────────────────────────────
def esc(text):
    """Escape XML special chars for ReportLab Paragraph."""
    return (text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
    )

def b(text):
    """Bold text."""
    return f'<b>{text}</b>'

def i(text):
    """Italic text."""
    return f'<i>{text}</i>'

def mono(text):
    """Monospace text."""
    return f'<font face="JetBrainsMono" size="9">{esc(text)}</font>'

def heading_with_content(heading_style, heading_text, body_text, body_style=None):
    """Create a KeepTogether block with heading + first paragraph."""
    bs = body_style or S['body']
    return g.KeepTogether([
        g.Paragraph(heading_text, heading_style),
        g.Paragraph(body_text, bs),
    ])

# ── Buffered heading system: headings are buffered and flushed with KeepTogether ──
_pending_heading = []  # list of flowables buffered from heading call

def _flush_heading():
    """Flush any pending heading elements directly (without KeepTogether)."""
    global _pending_heading
    if _pending_heading:
        for item in _pending_heading:
            story.append(item)
        _pending_heading = []

def _flush_heading_with(content_flowable):
    """Flush pending heading wrapped in KeepTogether with the content flowable."""
    global _pending_heading
    if _pending_heading:
        items = _pending_heading + [content_flowable]
        story.append(g.KeepTogether(items))
        _pending_heading = []
    else:
        story.append(content_flowable)

def _make_anchor(text):
    """Generate a safe anchor ID from heading text."""
    import re
    # Strip HTML tags
    clean = re.sub(r'<[^>]+>', '', text)
    # Extract the section number if present (e.g. "2.1" from "2.1 The Quantum Threat")
    m = re.match(r'^(\d+\.[\d.]*\s*|Appendix\s+[A-Z][\.:]\s*)', clean)
    if m:
        anchor = m.group(0).strip().rstrip('.').replace('.', '_').replace(' ', '_').replace(':', '')
        return f'sec_{anchor}'
    # Fallback: use first few words
    words = re.sub(r'[^a-zA-Z0-9\s]', '', clean).split()[:4]
    return 'sec_' + '_'.join(w.lower() for w in words)

def section_heading(text):
    """H1 heading with page break and anchor."""
    _flush_heading()  # flush any previous unbonded heading
    anchor = _make_anchor(text)
    story.append(g.PageBreak())
    _pending_heading.extend([
        g.Paragraph(f'<a name="{anchor}"/>{text}', S['h1']),
        g.AccentBar(cw, 1),
        g.Spacer(1, 12),
    ])

def sub_heading(text):
    """H2 heading with anchor."""
    _flush_heading()  # flush any previous unbonded heading
    anchor = _make_anchor(text)
    _pending_heading.extend([
        g.Spacer(1, 16),
        g.Paragraph(f'<a name="{anchor}"/>{text}', S['h2']),
        g.Spacer(1, 6),
    ])

def sub_sub_heading(text):
    """H3 heading with anchor."""
    _flush_heading()  # flush any previous unbonded heading
    anchor = _make_anchor(text)
    _pending_heading.extend([
        g.Spacer(1, 12),
        g.Paragraph(f'<a name="{anchor}"/>{text}', S['h3']),
        g.Spacer(1, 4),
    ])

def body(text):
    """Add body paragraph, bonded to any pending heading via KeepTogether."""
    _flush_heading_with(g.Paragraph(text, S['body']))

def body_small(text):
    """Add small body paragraph, bonded to any pending heading."""
    _flush_heading_with(g.Paragraph(text, S['body_small']))

def spacer(h=12):
    _flush_heading()
    story.append(g.Spacer(1, h))

def analogy(text):
    """Add analogy callout, bonded to any pending heading."""
    _flush_heading_with(g.CalloutBox(text, severity='note', title='ANALOGY'))

def info_box(text, title='KEY INSIGHT'):
    _flush_heading_with(g.CalloutBox(text, severity='info', title=title))

def warning_box(text, title='WARNING'):
    _flush_heading_with(g.CalloutBox(text, severity='warning', title=title))

def critical_box(text, title='CRITICAL'):
    _flush_heading_with(g.CalloutBox(text, severity='critical', title=title))

def code(text, lang='typescript'):
    _flush_heading_with(g.CodeBlock(text, language=lang))

def table(headers, rows, col_widths, highlight_cols=None):
    _flush_heading_with(g.CardTable(headers, rows, col_widths, width=cw, highlight_cols=highlight_cols))


# ══════════════════════════════════════════════════════════════════════════════
# COVER
# ══════════════════════════════════════════════════════════════════════════════
g.add_cover(
    story,
    'PERMAFROST',
    subtitle='Post-Quantum Threshold ML-DSA with Dealerless Key Generation',
    description='Post-quantum Encrypted Ring-based Multi-party Aggregated FROST\nA complete threshold signing protocol for the post-quantum era',
    version='v1.0',
    author='OP_NET Research Team',
    classification='Public',
    style='geometric',
)

# ══════════════════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS
# ══════════════════════════════════════════════════════════════════════════════
# Clickable TOC with internal links
# ══════════════════════════════════════════════════════════════════════════════
toc_entries = [
    ('1.', 'Abstract', False),
    ('2.', 'Introduction', False),
    ('2.1', 'The Quantum Threat', True),
    ('2.2', 'Why FROST and MuSig2 Die Under Quantum', True),
    ('2.3', 'What is ML-DSA?', True),
    ('2.4', 'The Fundamental Challenge', True),
    ('2.5', 'PERMAFROST: The Solution', True),
    ('3.', 'Account-Level Invisible Multisig', False),
    ('3.1', 'Your Account IS the Multisig', True),
    ('3.2', 'On-Chain Indistinguishability', True),
    ('3.3', 'Comparison: Smart Contract vs Account-Level', True),
    ('3.4', 'OPNet Integration', True),
    ('4.', 'Comparison with Existing Approaches', False),
    ('4.1', 'vs MuSig2', True),
    ('4.2', 'vs FROST', True),
    ('4.3', 'vs Smart Contract Multisig', True),
    ('4.4', 'Feature Matrix', True),
    ('5.', 'Mathematical Foundations', False),
    ('5.1', 'The Polynomial Ring', True),
    ('5.2', 'Number Theoretic Transform', True),
    ('5.3', 'Modular Arithmetic', True),
    ('5.4', 'Decomposition Functions', True),
    ('5.5', 'Sampling Functions', True),
    ('6.', 'ML-DSA (FIPS 204) Background', False),
    ('6.1', 'Parameters', True),
    ('6.2', 'Key Generation', True),
    ('6.3', 'Signing Algorithm', True),
    ('6.4', 'Verification', True),
    ('6.5', 'Why Threshold is Hard', True),
    ('7.', 'Threshold Construction Overview', False),
    ('7.1', 'Hyperball Masking', True),
    ('7.2', 'Additive Secret Sharing', True),
    ('7.3', 'Combinatorial Approach', True),
    ('8.', 'Key Generation Internals', False),
    ('8.1', 'How Shares Are Constructed', True),
    ('8.2', 'Gosper\'s Hack for Subset Enumeration', True),
    ('8.3', 'deriveUniformLeqEta', True),
    ('9.', 'Dealerless DKG: The PERMAFROST Key Ceremony', False),
    ('9.1', 'Design Decisions', True),
    ('9.2', 'Hard Invariants', True),
    ('9.3', 'Prerequisites', True),
    ('9.4', 'The Four Phases', True),
    ('9.7', 'Complaint and Abort Protocol', True),
    ('9.8', 'Security Proofs', True),
    ('10.', 'Hyperball Sampling', False),
    ('10.1', 'The sampleHyperball Algorithm', True),
    ('10.2', 'Box-Muller Transform', True),
    ('10.3', 'BigInt Precision', True),
    ('10.4', 'The C1 Fix', True),
    ('11.', 'Share Recovery', False),
    ('12.', 'The 3-Round Distributed Signing Protocol', False),
    ('12.1', 'Round 1: Commitment', True),
    ('12.2', 'Round 2: Reveal', True),
    ('12.3', 'Round 3: Partial Response', True),
    ('12.4', 'The H1 Timing Fix', True),
    ('13.', 'Combine: Signature Finalization', False),
    ('14.', 'Polynomial Packing: 23-Bit Encoding', False),
    ('15.', 'Parameter Tables', False),
    ('16.', 'Security Analysis and Hardening', False),
    ('17.', 'Frontend Integration: Communication Layer', False),
    ('18.', 'Float64 Precision Analysis', False),
    ('19.', 'Architecture and Implementation', False),
    ('20.', 'API Reference', False),
    ('21.', 'Known Limitations', False),
    ('A.', 'Notation Reference', False),
    ('B.', 'Test Coverage', False),
]

# Build clickable TOC
story.append(g.Paragraph("Table of Contents", S['h1']))
story.append(g.AccentBar(cw, 1))
story.append(g.Spacer(1, 16))

for num, title, is_sub in toc_entries:
    style = S['ts'] if is_sub else S['te']
    # Build anchor name matching what section_heading/sub_heading will produce
    num_clean = num.rstrip('.')
    anchor = 'sec_' + num_clean.replace('.', '_')
    # For appendix entries
    if num_clean in ('A', 'B'):
        anchor = f'sec_Appendix_{num_clean}'
    link_text = (
        f'<a href="#{anchor}" color="{g.Theme.ORANGE.hexval()}">{num}</a>'
        f'   <a href="#{anchor}" color="{g.Theme.text_primary().hexval()}">{title}</a>'
    )
    story.append(g.Paragraph(link_text, style))

story.append(g.PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 1. ABSTRACT
# ══════════════════════════════════════════════════════════════════════════════
story.append(g.Paragraph('<a name="sec_1"/>1. Abstract', S['h1']))
story.append(g.AccentBar(cw, 1))
spacer()

body(
    'PERMAFROST (<b>P</b>ost-quantum <b>E</b>ncrypted <b>R</b>ing-based <b>M</b>ulti-party '
    '<b>A</b>ggregated <b>FROST</b>) is a complete threshold signing protocol for the post-quantum era. '
    'Built on ML-DSA (FIPS 204), the NIST-standardized lattice-based digital signature scheme, '
    'PERMAFROST enables T-of-N parties to collaboratively produce a standard FIPS 204 signature '
    'without any single party holding the full signing key.'
)
spacer(8)
body(
    'The protocol consists of two major components: (1) a <b>dealerless distributed key generation</b> '
    '(DKG) ceremony where N parties jointly create an ML-DSA key pair with no trusted dealer, and '
    '(2) a <b>3-round distributed signing protocol</b> where any T parties independently generate '
    'their own randomness, exchange only commitments and responses, and produce a single standard '
    'FIPS 204 signature that is byte-for-byte indistinguishable from a single-signer signature.'
)
spacer(8)
body(
    'Key properties of PERMAFROST include: <b>post-quantum security</b> based on Module-LWE and '
    'Module-SIS hardness assumptions; <b>account-level invisible multisig</b> where the threshold '
    'key is indistinguishable from any standard ML-DSA public key; <b>structural secrecy</b> where '
    'no single party ever possesses the full secret key, even during key generation; <b>standard '
    'signature output</b> of 2,420 bytes (ML-DSA-44), 3,309 bytes (ML-DSA-65), or 4,627 bytes '
    '(ML-DSA-87) regardless of the threshold configuration; and support for all three NIST security '
    'levels (128-bit, 192-bit, 256-bit).'
)
spacer(8)
body(
    'PERMAFROST is the post-quantum successor to FROST (Flexible Round-Optimized Schnorr Threshold '
    'Signatures). Where FROST relies on the discrete logarithm problem and Schnorr signatures \u2014 '
    'both of which fall to quantum computers running Shor\'s algorithm \u2014 PERMAFROST rebuilds '
    'the same threshold functionality on lattice-based mathematics that quantum computers cannot crack. '
    'The protocol supports 2 \u2264 T \u2264 N \u2264 6 with empirically optimized parameters for all 45 '
    'valid (T, N, security level) configurations.'
)
spacer(8)
body(
    'While developed for OPNet\'s account-model blockchain, PERMAFROST is <b>chain-agnostic</b>. '
    'Any blockchain that adopts ML-DSA for post-quantum signatures \u2014 including Bitcoin itself '
    'when it inevitably migrates beyond ECDSA/Schnorr \u2014 can use PERMAFROST for invisible '
    'threshold multisig. The output is always a standard FIPS 204 signature. No protocol changes, '
    'no new opcodes, no consensus modifications required on the verifying chain.'
)
spacer(8)
info_box(
    'An interactive browser demo of the full PERMAFROST protocol (DKG + signing + verification) '
    'is available at:\n'
    'https://ipfs.opnet.org/ipfs/bafybeiejz5fc44scvp5qbgz4zzeg3jieccd5t7dwr6o3dqqhbk54czlhia/',
    title='LIVE DEMO'
)

# ══════════════════════════════════════════════════════════════════════════════
# 2. INTRODUCTION
# ══════════════════════════════════════════════════════════════════════════════
section_heading('2. Introduction')

sub_heading('2.1 The Quantum Threat to Threshold Signatures')

body(
    'The development of large-scale quantum computers poses an existential threat to the cryptographic '
    'foundations underlying all modern digital signature schemes. Shor\'s algorithm, when executed on a '
    'sufficiently powerful quantum computer, can solve the discrete logarithm problem and the integer '
    'factorization problem in polynomial time. These two mathematical problems form the security basis '
    'for ECDSA, EdDSA, Schnorr signatures, RSA, and every threshold signature scheme built on top of them.'
)
spacer(8)
body(
    'The implications for multi-party custody are severe. Every blockchain multisig system deployed today '
    '\u2014 Bitcoin\'s MuSig2, Ethereum\'s Gnosis Safe, Cosmos\'s on-chain multisig, OPNet\'s opMultisig '
    '\u2014 relies on elliptic curve cryptography (specifically secp256k1 or Ed25519) that a quantum '
    'computer can break. When quantum computers of sufficient scale arrive, the security of billions of '
    'dollars in multi-party custody arrangements will collapse simultaneously.'
)
spacer(8)
body(
    'NIST recognized this threat and spent eight years (2016\u20132024) evaluating post-quantum '
    'cryptographic algorithms. The result was FIPS 204, standardizing ML-DSA (Module Lattice-Based '
    'Digital Signature Algorithm, formerly CRYSTALS-Dilithium) as the primary post-quantum signature '
    'scheme. ML-DSA\'s security is based on the Module Learning With Errors (MLWE) and Module Short '
    'Integer Solution (MSIS) problems \u2014 lattice problems for which no efficient quantum algorithm '
    'is known.'
)

sub_heading('2.2 Why FROST and MuSig2 Die Under Quantum')

body(
    'FROST (Flexible Round-Optimized Schnorr Threshold, RFC 9591) and MuSig2 (BIP-327) are the '
    'state-of-the-art threshold and multi-signature schemes for pre-quantum cryptography. Both are '
    'elegant protocols that exploit a fundamental property of Schnorr signatures: <b>linearity</b>.'
)
spacer(8)
body(
    'In Schnorr signatures, the signature equation is s = r + c \u00b7 x, where r is the nonce, c is '
    'the challenge, and x is the secret key. This equation is perfectly linear: if multiple parties each '
    'hold a share x_i such that \u2211 x_i = x, they can each compute s_i = r_i + c \u00b7 x_i and '
    'sum the partial signatures to get s = \u2211 s_i = \u2211 r_i + c \u00b7 \u2211 x_i = r + c \u00b7 x. '
    'Threshold signing over Schnorr is almost trivial because of this linearity.'
)
spacer(8)
body(
    'Both FROST and MuSig2 depend entirely on the hardness of the discrete logarithm problem over '
    'elliptic curves. Shor\'s algorithm solves this problem in O(n\u00b3) time on a quantum computer, '
    'where n is the bit length of the group order. For secp256k1 (256-bit), this means a quantum '
    'computer with approximately 2,500 logical qubits could break these schemes in hours. While such '
    'quantum computers do not exist today, the trajectory of quantum computing research makes their '
    'eventual arrival a matter of "when," not "if."'
)

analogy(
    'If FROST is a house of cards built on mathematical assumptions that quantum computers can blow '
    'down, PERMAFROST is the same house rebuilt in reinforced concrete \u2014 same shape, same '
    'function, but the foundation is lattice-based mathematics that quantum computers cannot crack.'
)

sub_heading('2.3 What is ML-DSA (FIPS 204)?')

body(
    'ML-DSA (Module Lattice-Based Digital Signature Algorithm) is the NIST-standardized post-quantum '
    'signature scheme, published as FIPS 204 in August 2024. It is based on the CRYSTALS-Dilithium '
    'scheme, which was selected after eight years of rigorous evaluation by the global cryptographic '
    'community. ML-DSA operates in the polynomial ring R_q = \u2124_q[X]/(X\u00b2\u2075\u2076 + 1) '
    'where q = 8,380,417, using the "Fiat-Shamir with Aborts" paradigm.'
)
spacer(8)
body(
    'ML-DSA provides three security levels: <b>ML-DSA-44</b> (NIST Level 2, ~128-bit security), '
    '<b>ML-DSA-65</b> (NIST Level 3, ~192-bit security), and <b>ML-DSA-87</b> (NIST Level 5, '
    '~256-bit security). The signature sizes are 2,420 bytes, 3,309 bytes, and 4,627 bytes '
    'respectively \u2014 significantly larger than Schnorr (64 bytes) but still practical for '
    'blockchain applications.'
)

sub_heading('2.4 The Fundamental Challenge: Non-Linearity')

body(
    'The fundamental challenge in constructing threshold ML-DSA is that <b>ML-DSA is non-linear</b>. '
    'Unlike Schnorr, where the signature equation z = y + c \u00b7 s is perfectly linear, ML-DSA\'s '
    'signing process involves multiple non-linear operations that resist naive secret sharing:'
)
spacer(8)
body(
    '<b>1. Rejection sampling:</b> Standard ML-DSA rejects approximately 75% of signing attempts. '
    'The masking vector y must hide the secret s\u2081 via z = y + c \u00b7 s\u2081, but the norm '
    'check ||z||\u221e &lt; \u03b3\u2081 - \u03b2 depends on both y and the secret. In a threshold '
    'setting, parties must coordinate their rejection \u2014 if one party rejects, all must restart.'
)
spacer(4)
body(
    '<b>2. Decomposition functions:</b> HighBits, LowBits, MakeHint, and UseHint are all non-linear '
    'operations that cannot be computed independently on shares and then combined. These functions '
    'involve division, modular centering, and conditional logic that break under additive sharing.'
)
spacer(4)
body(
    '<b>3. Lattice structure:</b> The masking vector y must be jointly generated without any party '
    'learning the full y. Naive approaches (each party samples uniformly, then sum) do not produce '
    'the correct distribution for the sum to pass ML-DSA\'s norm checks.'
)
spacer(8)
body(
    'The "Threshold Signatures Reloaded" paper by Borin, Celi, del Pino, Espitau, Niot, and Prest '
    '(2025) solves these problems through a breakthrough construction: <b>hyperball sampling</b>. '
    'Instead of sampling y uniformly, each party independently samples a point on a high-dimensional '
    'hypersphere, and the sum of these samples has the correct statistical properties to pass all '
    'norm checks after rounding.'
)

sub_heading('2.5 PERMAFROST: The Complete Solution')

body(
    'PERMAFROST combines three components into a complete post-quantum threshold signing system:'
)
spacer(8)
body(
    '<b>1. Dealerless Distributed Key Generation (DKG):</b> A 4-phase protocol where N parties '
    'jointly create an ML-DSA key pair. No trusted dealer is required. Each party\'s share is derived '
    'from jointly-committed entropy via per-bitmask seed derivation, ensuring structural secrecy, '
    'forced randomness, and equivocation-immunity.'
)
spacer(4)
body(
    '<b>2. 3-Round Distributed Signing Protocol:</b> Any T parties independently generate their own '
    'randomness (on their own machine, disconnected), exchange commitments and responses over any '
    'communication channel, and produce a single standard FIPS 204 signature. No party\'s secret ever '
    'leaves their device.'
)
spacer(4)
body(
    '<b>3. Security Hardening:</b> All five audit findings from the Go reference implementation '
    '(C1, C8, H1, H6, M7) have been addressed, plus additional hardening including duplicate ID '
    'detection, constant-time commitment verification, state destruction classes, and failure-path '
    'cleanup.'
)

info_box(
    'PERMAFROST produces standard FIPS 204 signatures that any ML-DSA verifier can validate. '
    'The signature size is ALWAYS the standard size (2,420 / 3,309 / 4,627 bytes) regardless '
    'of the threshold configuration (T, N). A verifier cannot distinguish a PERMAFROST threshold '
    'signature from a single-signer ML-DSA signature.',
    title='KEY PROPERTY'
)

# ══════════════════════════════════════════════════════════════════════════════
# 3. ACCOUNT-LEVEL INVISIBLE MULTISIG
# ══════════════════════════════════════════════════════════════════════════════
section_heading('3. Account-Level Invisible Multisig')

sub_heading('3.1 Your Account IS the Multisig')

body(
    'In account-model blockchains like OPNet, every account is identified by its ML-DSA public key. '
    'With threshold ML-DSA, the public key can be a <b>threshold key</b> \u2014 one that requires '
    'T-of-N parties to sign \u2014 while looking identical to any other ML-DSA public key on-chain. '
    'This is not a smart contract multisig. This is <b>the account itself being a multisig</b>.'
)
spacer(8)
body(
    'The distinction is fundamental. Smart contract multisig operates at the application layer: a '
    'contract receives N individual signatures, verifies each one on-chain, counts that at least T '
    'are valid, then executes the transaction. Account-level threshold operates below the contract '
    'layer: T parties coordinate off-chain to produce a single signature, and the blockchain sees '
    'one address, one signature, one transaction \u2014 identical to any other account.'
)

analogy(
    'Think of smart contract multisig as a lockbox where everyone puts their key in separate slots '
    'visibly on camera. Account-level threshold is more like a single lock that secretly requires '
    'multiple people to turn simultaneously \u2014 but from the outside, it looks and works like '
    'any other lock.'
)

sub_heading('3.2 On-Chain Indistinguishability')

body(
    'This is the critical property: <b>no on-chain observer can determine whether a signature was '
    'produced by a single signer or by a threshold group</b>. The threshold configuration (T, N) '
    'is completely invisible on-chain.'
)
spacer(8)

table(
    ['Property', 'Single-Signer ML-DSA', 'PERMAFROST Threshold'],
    [
        ['Public key size', '1,312 / 1,952 / 2,592 bytes', 'Identical'],
        ['Signature size', '2,420 / 3,309 / 4,627 bytes', 'Identical'],
        ['Verification algorithm', 'Standard FIPS 204', 'Identical'],
        ['On-chain format', 'Standard encoding', 'Identical'],
        ['tx.origin', 'Signer\'s public key', 'Aggregated threshold key'],
        ['Distinguishable?', 'N/A', 'NO \u2014 mathematically identical'],
    ],
    [0.25, 0.35, 0.40],
)

sub_heading('3.3 Comparison: Smart Contract vs Account-Level')

table(
    ['Capability', 'Smart Contract Multisig', 'Account-Level Threshold'],
    [
        ['Contract deployer', 'Single key (SPOF)', 'Threshold group (no single compromise)'],
        ['Token admin keys', 'N-of-N via on-chain logic', 'N-of-N via aggregated key \u2014 invisible'],
        ['Transaction signing', 'Multiple sigs verified on-chain', 'One signature, zero overhead'],
        ['tx.origin', 'One signer\'s address', 'Aggregated identity'],
        ['Visibility', 'On-chain \u2014 anyone sees multisig', 'Invisible \u2014 looks like normal account'],
        ['Gas cost', 'Verifying N signatures + logic', 'Verifying 1 signature (standard)'],
        ['Scope', 'Only supported operations', 'EVERY operation'],
        ['Key custody', 'N independent keys', 'N shares; secret key never exists in one place'],
    ],
    [0.18, 0.38, 0.44],
)

sub_heading('3.4 OPNet Integration')

body(
    'OPNet uses an account model where every account is identified by its ML-DSA key. With PERMAFROST, '
    '<b>the account itself becomes the multisig</b> \u2014 not at the contract level, not at the '
    'application level, but at the account level. Below the contract. Below everything.'
)
spacer(8)
body(
    'This works for <b>every operation on OPNet</b>: deployments, token transfers, admin calls, '
    'parameter changes, contract upgrades \u2014 everything. Because the multisig lives at the '
    'account level, every transaction from that address inherits threshold protection automatically. '
    'No smart contract logic needed. No on-chain multisig overhead. Just one address, one signature.'
)
spacer(8)

code('''// Corporate treasury: 4-of-6 dealerless key ceremony
const th = ThresholdMLDSA.create(87, 4, 6);  // NIST Level 5, maximum security
const sessionId = randomBytes(32);

// Phase 1: Each board member commits entropy on their own device
const p1 = th.dkgPhase1(myPartyId, sessionId);
// broadcast p1.broadcast to all parties...

// Phase 2: Reveal entropy, derive shared secrets per-bitmask
const p2 = th.dkgPhase2(myPartyId, sessionId, p1.state, allPhase1);
// broadcast p2.broadcast, send p2.privateToHolders via encrypted channel...

// Phase 2 Finalize + Phase 3: Verify, derive shares, distribute masks
const p2f = th.dkgPhase2Finalize(myPartyId, sessionId, p1.state, 
    allPhase1, allPhase2, receivedReveals);
// send mask pieces via encrypted channel...

// Phase 4: Aggregate masks, derive public key
const p4 = th.dkgPhase4(myPartyId, setup.bitmasks, p2f.generatorAssignment,
    receivedMasks, p2f.ownMaskPieces);
// broadcast p4...

// Finalize: everyone computes the same public key
const { publicKey, share } = th.dkgFinalize(myPartyId, p2f.rho, allPhase4, p2f.shares);
// publicKey -> OPNet/Bitcoin address. Nobody ever saw the full secret.
// share -> stored on this device only. 4 of 6 needed to sign.''')

spacer(8)
body(
    '<b>Why this matters for post-quantum \u2014 and for Bitcoin:</b> Every chain\'s multisig today '
    'is built on pre-quantum cryptography. Bitcoin MuSig2: Schnorr-based \u2014 dead when quantum '
    'arrives. Ethereum Safe: ECDSA-based \u2014 dead. Cosmos multisig: secp256k1 \u2014 dead.'
)
spacer(8)
body(
    'PERMAFROST is the <b>first account-level threshold multisig that survives quantum computers</b>, '
    'based on a NIST-standardized algorithm, producing signatures any ML-DSA verifier can validate. '
    'This is not limited to OPNet \u2014 <b>any blockchain that adopts ML-DSA can use PERMAFROST</b> '
    'for invisible threshold signing. Bitcoin itself, when it eventually migrates to post-quantum '
    'signatures, will need exactly this: aggregated ML-DSA multisig where the output is a single '
    'standard signature indistinguishable from a solo signer. PERMAFROST is that solution.'
)

# ══════════════════════════════════════════════════════════════════════════════
# 4. COMPARISON WITH EXISTING APPROACHES
# ══════════════════════════════════════════════════════════════════════════════
section_heading('4. Comparison with Existing Approaches')

sub_heading('4.1 vs MuSig2 (Bitcoin Schnorr)')

body(
    'MuSig2 is the state-of-the-art for Bitcoin Schnorr key aggregation (N-of-N). It achieves elegant '
    '2-round signing by exploiting Schnorr\'s linearity. However, MuSig2 is fundamentally limited: '
    'it only supports N-of-N (all parties must sign), and it relies entirely on the discrete logarithm '
    'problem over secp256k1, which Shor\'s algorithm destroys.'
)

sub_heading('4.2 vs FROST (Schnorr Threshold)')

body(
    'FROST (RFC 9591) extends Schnorr aggregation to T-of-N thresholds using Shamir secret sharing. '
    'It achieves 2-round signing with beautiful simplicity. But like MuSig2, FROST\'s security depends '
    'entirely on the discrete logarithm problem. PERMAFROST is the conceptual successor to FROST: '
    'same T-of-N threshold signing, same invisible on-chain signature, but built on post-quantum '
    'lattice foundations.'
)

sub_heading('4.3 vs Smart Contract Multisig')

body(
    'Smart contract multisig (Gnosis Safe, opMultisig, etc.) operates at the application layer. '
    'It verifies N individual signatures on-chain, costs O(N) gas, is visible to everyone as multisig, '
    'and only works for operations the contract explicitly supports. PERMAFROST operates below the '
    'contract layer with O(1) verification cost and universal scope.'
)

sub_heading('4.4 Feature Matrix')

table(
    ['Property', 'MuSig2', 'FROST', 'SC Multisig', 'PERMAFROST'],
    [
        ['Threshold', 'N-of-N only', 'T-of-N', 'T-of-N', 'T-of-N'],
        ['Signing rounds', '2', '2', '1 (on-chain)', '3'],
        ['Quantum-safe', 'No', 'No', 'No', 'YES (FIPS 204)'],
        ['Signature size', '64 bytes', '64 bytes', 'N \u00d7 sig', '2,420-4,627 bytes'],
        ['On-chain visible', 'No', 'No', 'Yes', 'No'],
        ['Verification cost', 'O(1)', 'O(1)', 'O(N)', 'O(1)'],
        ['Math basis', 'Discrete log', 'Discrete log', 'Varies', 'MLWE + MSIS'],
        ['Standard', 'BIP-327', 'RFC 9591', 'N/A', 'FIPS 204'],
        ['Scope', 'Signing', 'Signing', 'Limited', 'ALL operations'],
        ['DKG', 'None needed', '2-round', 'N/A', '4-phase dealerless'],
    ],
    [0.18, 0.16, 0.16, 0.20, 0.30],
)

spacer(12)
info_box(
    'Why 3 rounds instead of 2? ML-DSA\'s non-linearity (rejection sampling, decomposition) '
    'requires stronger commitment binding than Schnorr\'s linear structure. The commit-then-reveal '
    'pattern prevents adaptive manipulation of the combined commitment. The 3rd round also enables '
    'commitment hash verification, catching cheating parties before they can corrupt the signature.',
    title='WHY 3 ROUNDS?'
)

# ══════════════════════════════════════════════════════════════════════════════
# 5. MATHEMATICAL FOUNDATIONS
# ══════════════════════════════════════════════════════════════════════════════
section_heading('5. Mathematical Foundations')

sub_heading('5.1 The Polynomial Ring R_q')

body(
    'All arithmetic in PERMAFROST operates in the polynomial ring:'
)
spacer(4)
body(
    '<b>R_q = \u2124_q[X] / (X\u00b2\u2075\u2076 + 1)</b>'
)
spacer(4)
body(
    'where <b>q = 8,380,417</b> (the Dilithium prime, 23 bits: 2\u00b2\u00b3 - 2\u00b9\u00b3 + 1) '
    'and <b>N = 256</b> (polynomial degree). Elements of R_q are polynomials of degree \u2264 255 '
    'with coefficients in \u2124_q = {0, 1, ..., q-1}.'
)
spacer(8)
body(
    'This ring is chosen for three critical reasons: (1) q \u2261 1 (mod 2N), enabling efficient '
    'Number Theoretic Transform; (2) X\u00b2\u2075\u2076 + 1 is the 512th cyclotomic polynomial, '
    'irreducible over \u2124, ensuring the ring has the correct algebraic structure; and (3) the '
    'resulting ring is isomorphic (via NTT) to \u2124_q\u00b2\u2075\u2076, making pointwise '
    'multiplication possible in O(N log N) time instead of O(N\u00b2).'
)

analogy(
    'The polynomial ring is like a clock face, but instead of 12 hours it has 8,380,417 positions, '
    'and instead of one hand it has 256 hands all spinning simultaneously. Every operation in '
    'PERMAFROST happens on this multi-handed clock.'
)

sub_heading('5.2 Number Theoretic Transform (NTT)')

body(
    'The NTT is the finite-field analogue of the Fast Fourier Transform. It maps polynomials from '
    'their coefficient representation to their evaluation representation:'
)
spacer(4)
body(
    '<b>NTT: R_q \u2192 \u2124_q\u00b2\u2075\u2076</b>'
)
spacer(4)
body(
    'Given a primitive 512th root of unity \u03b6 = 1753 in \u2124_q (i.e., \u03b6\u2075\u00b9\u00b2 '
    '\u2261 1 mod q and \u03b6\u00b2\u2075\u2076 \u2261 -1 mod q), the NTT of a polynomial a is:'
)
spacer(4)
body(
    'NTT(a)[i] = \u2211_{j=0}\u00b2\u2075\u2075 a[j] \u00b7 \u03b6^{brv(i) \u00b7 (2j+1)} mod q'
)
spacer(8)
body(
    'where brv(i) is the 8-bit bit-reversal of i. In NTT domain, polynomial multiplication is '
    'pointwise: NTT(a \u00b7 b) = NTT(a) \u2299 NTT(b). This is critical for threshold signing '
    'performance, as computing A\u00b7z, c\u00b7s, etc. requires many polynomial multiplications.'
)
spacer(8)
body(
    '<b>Implementation note:</b> Since q is 23 bits, the product a[i]\u00b7b[i] is at most 46 bits. '
    'JavaScript\'s Number type provides 53 bits of integer precision (IEEE 754 double), so all NTT '
    'arithmetic stays within safe integer range. This avoids the need for BigInt in ring operations '
    '\u2014 a critical performance decision.'
)

sub_heading('5.3 Modular Arithmetic')

body(
    'Two modular reduction functions are used throughout:'
)
spacer(4)
body(
    '<b>mod(a, q):</b> Standard unsigned reduction to [0, q): mod(a) = ((a % q) + q) % q'
)
spacer(4)
body(
    '<b>smod(a, q):</b> Centered/signed reduction to [-(q-1)/2, (q-1)/2]: '
    'smod(a) = mod(a + (q-1)/2) - (q-1)/2'
)
spacer(8)
body(
    'The centered form is essential for norm checks (e.g., polyChknorm) where we need to test if '
    'coefficients are "small" \u2014 checking |smod(a[i])| &lt; B requires centering around zero.'
)

sub_heading('5.4 Decomposition Functions')

body(
    'ML-DSA uses several decomposition functions parameterized by \u03b3\u2082 (gamma_2):'
)
spacer(8)
body(
    '<b>Power2Round(r):</b> Splits r into high and low parts relative to 2^d (d=13). '
    'r\u2080 = smod(r, 2^d), r\u2081 = (r - r\u2080) / 2^d. '
    'Used to split the public key: t = t\u2081 \u00b7 2^d + t\u2080.'
)
spacer(4)
body(
    '<b>Decompose(r):</b> Splits r relative to 2\u03b3\u2082. '
    'r\u2080 = smod(r, 2\u03b3\u2082), r\u2081 = (r - r\u2080) / (2\u03b3\u2082). '
    'Special case: if r - r\u2080 = q-1, return (r\u2081=0, r\u2080=r\u2080-1).'
)
spacer(4)
body(
    '<b>HighBits(r)</b> = Decompose(r).r\u2081, '
    '<b>LowBits(r)</b> = Decompose(r).r\u2080.'
)
spacer(4)
body(
    '<b>MakeHint(z, r):</b> Returns 1 if adding z to r changes HighBits. '
    '<b>UseHint(h, r):</b> Adjusts HighBits according to hint h. '
    'These are central to how ML-DSA achieves signature compression.'
)

sub_heading('5.5 Sampling Functions')

body(
    '<b>RejNTTPoly(xof):</b> Samples a uniformly random polynomial in NTT domain by rejection '
    'sampling from SHAKE-128. Each 3-byte block yields a 23-bit candidate; values \u2265 q are rejected.'
)
spacer(4)
body(
    '<b>RejBoundedPoly(xof):</b> Samples a polynomial with small coefficients in [-\u03b7, \u03b7] '
    'by rejection sampling from SHAKE-256. For \u03b7=2, each nibble yields a candidate via '
    '\u03b7 - (t mod 5) for t &lt; 15.'
)
spacer(4)
body(
    '<b>SampleInBall(seed):</b> Samples a sparse polynomial c \u2208 R_q with exactly \u03c4 nonzero '
    'coefficients, each \u00b11. This is the challenge polynomial in the Fiat-Shamir transform.'
)

# ══════════════════════════════════════════════════════════════════════════════
# 6. ML-DSA (FIPS 204) BACKGROUND
# ══════════════════════════════════════════════════════════════════════════════
section_heading('6. ML-DSA (FIPS 204) Background')

sub_heading('6.1 Standard Parameters')

table(
    ['Parameter', 'ML-DSA-44', 'ML-DSA-65', 'ML-DSA-87'],
    [
        ['NIST Level', '2 (128-bit)', '3 (192-bit)', '5 (256-bit)'],
        ['K (rows of A)', '4', '6', '8'],
        ['L (columns of A)', '4', '5', '7'],
        ['\u03b7 (secret bound)', '2', '4', '2'],
        ['\u03c4 (challenge weight)', '39', '49', '60'],
        ['\u03b3\u2081 (masking range)', '2\u00b9\u2077', '2\u00b9\u2079', '2\u00b9\u2079'],
        ['\u03b3\u2082 (decomposition)', '(q-1)/88', '(q-1)/32', '(q-1)/32'],
        ['\u03c9 (hint weight)', '80', '55', '75'],
        ['\u03b2 = \u03c4\u00b7\u03b7', '78', '196', '120'],
        ['d (Power2Round)', '13', '13', '13'],
        ['c\u0303 bytes', '32', '48', '64'],
        ['Public key bytes', '1,312', '1,952', '2,592'],
        ['Signature bytes', '2,420', '3,309', '4,627'],
    ],
    [0.28, 0.24, 0.24, 0.24],
)

sub_heading('6.2 Key Generation')

body(
    'Standard ML-DSA key generation proceeds as follows:'
)
spacer(4)
body(
    '1. Sample \u03c1 (public seed, 32 bytes), \u03c1\' (secret seed), K (signing key) from random seed via SHAKE-256.'
)
body(
    '2. Expand A \u2208 R_q^{K\u00d7L} from \u03c1 using XOF-128 (SHAKE-128).'
)
body(
    '3. Sample s\u2081 \u2208 R_q^L, s\u2082 \u2208 R_q^K with small coefficients (bound \u03b7) via rejection sampling.'
)
body(
    '4. Compute t = A \u00b7 s\u2081 + s\u2082 in R_q^K.'
)
body(
    '5. Split t into (t\u2081, t\u2080) via Power2Round.'
)
body(
    '6. Public key: pk = Encode(\u03c1, t\u2081). Secret key: sk = (\u03c1, K, tr, s\u2081, s\u2082, t\u2080) '
    'where tr = SHAKE-256(pk).'
)

sub_heading('6.3 Signing Algorithm (Rejection Sampling Loop)')

body(
    'The ML-DSA signing algorithm uses a "Fiat-Shamir with Aborts" paradigm, where most signing '
    'attempts are rejected to ensure the signature does not leak information about the secret key:'
)
spacer(4)
body(
    '1. Compute message representative: \u03bc = SHAKE-256(tr || M).'
)
body(
    '2. Derive private randomness: \u03c1\' = SHAKE-256(K || rnd || \u03bc).'
)
body(
    '3. Sample masking vector y \u2208 R_q^L with coefficients in [-\u03b3\u2081+1, \u03b3\u2081].'
)
body(
    '4. Compute w = A \u00b7 y, then w\u2081 = HighBits(w).'
)
body(
    '5. Compute challenge: c\u0303 = SHAKE-256(\u03bc || W1Encode(w\u2081)), c = SampleInBall(c\u0303).'
)
body(
    '6. Compute response: z = y + c \u00b7 s\u2081.'
)
body(
    '7. <b>Reject</b> if ||z||\u221e \u2265 \u03b3\u2081 - \u03b2 or '
    '||LowBits(w - c \u00b7 s\u2082)||\u221e \u2265 \u03b3\u2082 - \u03b2.'
)
body(
    '8. Compute hint h = MakeHint(-c \u00b7 t\u2080, w - c \u00b7 s\u2082 + c \u00b7 t\u2080). '
    'Reject if weight(h) &gt; \u03c9.'
)
body(
    '9. Output signature: \u03c3 = (c\u0303, z, h).'
)

sub_heading('6.4 Verification')

body(
    'Verification is straightforward: decode public key (\u03c1, t\u2081) and signature (c\u0303, z, h), '
    'check ||z||\u221e &lt; \u03b3\u2081 - \u03b2, compute c = SampleInBall(c\u0303), '
    'w\'_approx = A \u00b7 z - c \u00b7 t\u2081 \u00b7 2^d, '
    'w\'\u2081 = UseHint(h, w\'_approx), then verify c\u0303 = SHAKE-256(\u03bc || W1Encode(w\'\u2081)).'
)

sub_heading('6.5 Why Threshold is Hard for ML-DSA')

body(
    'Unlike Schnorr/ECDSA where threshold signing is relatively straightforward (linear secret sharing '
    '+ linear signature equation), ML-DSA has three fundamental obstacles:'
)
spacer(8)

critical_box(
    '1. REJECTION SAMPLING: ~75% of signing attempts are rejected. With threshold signing, parties '
    'must coordinate their rejection \u2014 if one party rejects, all must restart.\n\n'
    '2. NON-LINEAR OPERATIONS: Decomposition functions (HighBits, LowBits, MakeHint) cannot be '
    'computed independently on shares and then combined.\n\n'
    '3. JOINT MASKING: The masking vector y must be jointly generated without any party learning '
    'the full y, while still producing a valid distribution for the sum.',
    title='FUNDAMENTAL OBSTACLES'
)

spacer(8)
body(
    'The "Threshold Signatures Reloaded" paper solves these using: <b>hyperball sampling</b> (replace '
    'uniform y with a continuous sphere distribution), <b>additive secret sharing over bitmasks</b>, '
    'and <b>parallel iterations</b> (K_iter independent attempts per round to amortize rejection).'
)

# ══════════════════════════════════════════════════════════════════════════════
# 7. THRESHOLD CONSTRUCTION OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
section_heading('7. Threshold Construction Overview')

sub_heading('7.1 High-Level Protocol Flow')

body(
    'The PERMAFROST protocol has two major phases: <b>key generation</b> (one-time setup) and '
    '<b>distributed signing</b> (per transaction). Key generation produces a standard ML-DSA public '
    'key and N threshold key shares. Distributed signing uses any T shares to produce a standard '
    'FIPS 204 signature via three rounds of communication.'
)

sub_heading('7.2 The Hyperball Masking Breakthrough')

body(
    'Instead of sampling y uniformly from [-\u03b3\u2081+1, \u03b3\u2081]^{N\u00b7L} as in standard '
    'ML-DSA, the threshold protocol:'
)
spacer(4)
body(
    '1. Samples a point on a high-dimensional hypersphere (radius r\') using Box-Muller + normalization.'
)
body(
    '2. Rounds the continuous samples to get integer vectors (y, e).'
)
body(
    '3. Computes w = A \u00b7 y + e (instead of w = A \u00b7 y).'
)
spacer(8)
body(
    'This continuous sampling enables additive sharing: each party samples independently on the '
    'hypersphere, and the sum of their samples is "well-shaped" enough to pass the norm checks '
    'after rounding. The error term e absorbs the rounding differences.'
)

analogy(
    'Imagine you need to bake a cake, but no single person is allowed to know the full recipe. '
    'Hyperball sampling is like having each baker add ingredients by feel \u2014 measured from a '
    'carefully calibrated internal compass \u2014 such that the combined result always tastes '
    'correct, even though no baker knew the exact quantities anyone else added.'
)

sub_heading('7.3 Additive Secret Sharing over Bitmasks')

body(
    'The secret key (s\u2081, s\u2082) is split into additive shares indexed by <b>bitmasks</b>. '
    'For a (T, N) configuration, we enumerate all C(N, N-T+1) subsets of (N-T+1) potentially honest '
    'signers. Each subset corresponds to a bitmask, and for each bitmask, a separate additive share '
    'is generated.'
)
spacer(8)
body(
    'Each party stores shares for all subsets they belong to. A "share recovery" algorithm combines '
    'the right shares based on which T parties are active. This combinatorial approach ensures that '
    'any T parties can sign, even though the underlying sharing is additive (not Shamir-based).'
)
spacer(8)
body(
    'For example, in a 3-of-5 configuration: C(5, 3) = 10 honest-signer subsets. Each party belongs '
    'to C(4, 2) = 6 of these subsets. The total secret s\u2081 = \u2211 s\u2081^{(hs)} over all 10 '
    'subsets. When 3 specific parties want to sign, the share recovery algorithm selects the right '
    'combination of stored shares for each party.'
)

# ══════════════════════════════════════════════════════════════════════════════
# 8. KEY GENERATION INTERNALS
# ══════════════════════════════════════════════════════════════════════════════
section_heading('8. Key Generation Internals')

sub_heading('8.1 How Shares Are Constructed (3-of-5 Example)')

body(
    'This section explains the mathematics of how threshold key shares are constructed. '
    'The dealerless DKG (Section 9) distributes this process across all parties so no single '
    'entity ever sees the full picture. Understanding the underlying math is essential for '
    'understanding why the DKG is secure.'
)
spacer(8)
body(
    '<b>Step 1: Seed generation.</b> The dealer generates a 32-byte random seed. This is the only '
    'source of randomness \u2014 everything else is deterministic from this seed.'
)
spacer(4)
body(
    '<b>Step 2: SHAKE-256 expansion.</b> The seed is fed into SHAKE-256(seed || K || L). First 32 bytes '
    'of output \u2192 \u03c1 (public randomness for matrix A). Then 5 \u00d7 32 bytes \u2192 one '
    'key per party (per-party randomness).'
)
spacer(4)
body(
    '<b>Step 3: Matrix A expansion.</b> A is a 4\u00d74 matrix of polynomials (for ML-DSA-44). '
    'Each polynomial has 256 coefficients in \u2124_q. Expansion uses SHAKE-128 with rejection sampling.'
)
spacer(4)
body(
    '<b>Step 4: Gosper\'s hack enumerates all subsets.</b> For T=3, N=5, we need N\u2212T+1 = 3 signers '
    'in each honest subset. C(5,3) = 10 such subsets, each represented as a 5-bit bitmask.'
)

sub_heading('8.2 Gosper\'s Hack for Subset Enumeration')

body(
    'Gosper\'s hack iterates through all bitmasks with exactly k bits set, in ascending order, '
    'using only bitwise arithmetic:'
)

code('''let honestSigners = (1 << (N - T + 1)) - 1;  // smallest bitmask
while (honestSigners < (1 << N)) {
  // Process this subset...
  const c = honestSigners & -honestSigners;     // lowest set bit
  const r = honestSigners + c;                  // carry propagation
  honestSigners = (((r ^ honestSigners) >> 2) / c) | r;
}''')

spacer(8)
body(
    '<b>Step 5: For each subset, sample a secret share.</b> The SHAKE-256 stream produces a 64-byte '
    'share seed for each subset. From this seed, deriveUniformLeqEta samples s\u2081 (L polynomials) '
    'and s\u2082 (K polynomials), each with 256 coefficients in [-\u03b7, \u03b7].'
)
spacer(4)
body(
    '<b>Step 6: Accumulate the total secret.</b> All 10 shares\' s\u2081 vectors are summed (mod q) '
    'to get totalS\u2081. Same for s\u2082. No single party knows this total.'
)
spacer(4)
body(
    '<b>Step 7: Compute public key.</b> t = A \u00b7 NTT(totalS\u2081) + totalS\u2082, split via '
    'Power2Round into (t\u2081, t\u2080). pk = Encode(\u03c1, t\u2081) \u2014 standard FIPS 204 '
    'format, 1,312 bytes. tr = SHAKE-256(pk, 64).'
)
spacer(4)
body(
    '<b>Step 8: Distribute shares.</b> Each party receives their ThresholdKeyShare containing: '
    'party ID, \u03c1, per-party key, tr, and a map from bitmask to (s\u2081, s\u2082, s\u0302\u2081, '
    's\u0302\u2082) for all subsets containing that party.'
)

info_box(
    'In the dealerless DKG (Section 9), each of these steps is distributed across all parties. '
    'No single party performs the full computation \u2014 each party contributes entropy per-bitmask, '
    'and shares are derived jointly so nobody ever sees the full secret. The math is identical; '
    'only the trust model changes from centralized to fully distributed.',
    title='FROM MATH TO PRACTICE'
)

sub_heading('8.3 deriveUniformLeqEta')

body(
    'This function samples a polynomial with small coefficients in [-\u03b7, \u03b7] from a 64-byte '
    'seed. It uses SHAKE-256 (not SHAKE-128 as in standard ML-DSA) with input: seed[0:64] || nonce_le16.'
)
spacer(4)
body(
    'For \u03b7=2: each nibble t &lt; 15 yields coefficient Q + \u03b7 - (t - floor(205\u00b7t/1024)\u00b75). '
    'The magic constant floor(205\u00b7t/1024) computes floor(t/5) without division for t &lt; 15.'
)
spacer(4)
body(
    'For \u03b7=4: each nibble t \u2264 2\u03b7 yields coefficient Q + \u03b7 - t.'
)

# ══════════════════════════════════════════════════════════════════════════════
# 9. DEALERLESS DKG: THE PERMAFROST KEY CEREMONY
# ══════════════════════════════════════════════════════════════════════════════
section_heading('9. Dealerless DKG: The PERMAFROST Key Ceremony')

body(
    'The dealerless distributed key generation is the core innovation of PERMAFROST beyond the signing '
    'protocol. It eliminates the trusted dealer entirely, achieving all four critical properties '
    'simultaneously: <b>no trusted dealer</b>, <b>structural secrecy</b>, <b>forced randomness</b>, '
    'and <b>minimal public leakage</b>.'
)

analogy(
    'The dealerless DKG is like a group of people mixing paint together. Each person adds their '
    'secret color to each bucket. Nobody knows what color the others added. But because they all '
    'committed to their colors beforehand (sealed envelopes), nobody can cheat. The final mixed '
    'color is the public key \u2014 everyone can see it, but nobody knows the individual contributions.'
)

sub_heading('9.1 Design Decisions: Per-Bitmask Seed Derivation')

body(
    'Three approaches were considered for dealerless key generation:'
)
spacer(8)

table(
    ['Property', 'Global Seed', 'Per-Generator Local', 'Per-Bitmask Seed (chosen)'],
    [
        ['Structural secrecy', 'No (all know S)', 'Yes', 'Yes'],
        ['Unbiased shares', 'Yes', 'No', 'Yes (honest minority)'],
        ['No equivocation', 'Yes (deterministic)', 'No (needs complaints)', 'Yes (deterministic)'],
        ['No sabotage', 'Yes', 'No', 'Yes'],
        ['Honest-party req', '1 of N', 'N/A', '1 per bitmask subgroup'],
    ],
    [0.20, 0.20, 0.25, 0.35],
)

spacer(8)
body(
    '<b>Core idea:</b> For each bitmask b, the holders of b jointly derive seed_b via a mini coin-flip. '
    'Shares are then deterministically derived from seed_b. This gives structural secrecy (non-holders '
    'never learn seed_b), forced randomness (unbiased if at least one holder is honest), no equivocation '
    '(all holders independently compute the same share), and no sabotage (shares forced by the jointly-determined seed).'
)

sub_heading('9.2 Hard Invariants')

critical_box(
    'I1: Global rho is used ONLY for matrix A expansion and generator assignment. No share material '
    'is ever derived from global rho.\n\n'
    'I2: Every share (s1^b, s2^b) is derived from seed_b, which is known ONLY to holders of b. '
    'Non-holders never see seed_b, its inputs, or the resulting share. This is a structural guarantee '
    '\u2014 it does not depend on any party deleting data.',
    title='HARD INVARIANTS'
)

sub_heading('9.3 Prerequisites')

body(
    '<b>P1. Authenticated confidential channels (REQUIRED):</b> Pairwise authenticated + encrypted '
    'channels between all parties. Without confidential channels, the protocol provides NO security '
    'guarantees. Required for bitmask seed reveals and mask piece delivery.'
)
spacer(4)
body(
    '<b>P2. Broadcast channel:</b> Reliable broadcast visible to all parties. Required for commitments, '
    '\u03c1 reveals, and aggregates.'
)
spacer(4)
body(
    '<b>P3. Liveness:</b> All N parties must complete all phases. Abort \u2192 restart with new session ID.'
)

sub_heading('9.4 The Four Phases')

# ── Phase 1 ──
_flush_heading_with(g.StepIndicator(1, 'Phase 1: Commit',
    'Each party independently samples entropy, computes commitment hashes, and broadcasts them.'))
spacer(4)

body('Each party i independently:')
spacer(4)
body('\u2022 Samples <b>rho_i</b> \u2014 256-bit entropy for the public matrix seed.')
spacer(4)
body('\u2022 For each bitmask b where i is a holder: samples <b>r_{i,b}</b> \u2014 256-bit entropy contribution.')
spacer(4)
body('\u2022 Computes and <b>broadcasts</b> commitment hashes:')
spacer(4)
code('C_i^rho  = SHAKE-256("DKG-RHO-COMMIT"   || sid || i || rho_i)\nC_{i,b}  = SHAKE-256("DKG-BSEED-COMMIT" || sid || b || i || r_{i,b})', lang='')
spacer(4)
body('All parties collect all Phase 1 broadcasts before proceeding.')

# ── Phase 2 ──
_flush_heading_with(g.StepIndicator(2, 'Phase 2: Reveal & Derive',
    'Parties reveal entropy, verify commitments, derive joint matrix and per-bitmask seeds.'))
spacer(4)

body('<b>Step 2a:</b> Each party broadcasts rho_i. All verify against C_i^rho. Abort if mismatch.')
spacer(4)
body('<b>Step 2b:</b> For each bitmask b, party i sends r_{i,b} to fellow holders via confidential channel.')
spacer(4)
body('<b>Step 2c:</b> Each holder verifies received r_{i,b} against C_{i,b}. Abort if mismatch.')
spacer(4)
body(
    '<b>Step 2d:</b> Derive joint rho:'
)
code('rho = SHAKE-256("DKG-RHO-AGG" || sid || rho_0 || ... || rho_{N-1})', lang='')
spacer(4)
body('Expand matrix A from rho via XOF-128. Assign generators per bitmask using balanced deterministic assignment.')
spacer(4)
body(
    '<b>Step 2e:</b> Each holder of bitmask b independently computes:'
)
code('seed_b = SHAKE-256("DKG-BSEED" || sid || b || r_{p0,b} || ... || r_{pk,b})\n\nfor j = 0..L-1:  s1^b[j] = deriveUniformLeqEta(seed_b, j)\nfor j = 0..K-1:  s2^b[j] = deriveUniformLeqEta(seed_b, j + L)', lang='')
spacer(4)
body('All holders of b arrive at the identical share \u2014 no distribution needed.')

# ── Phase 3 ──
_flush_heading_with(g.StepIndicator(3, 'Phase 3: Masked Aggregation',
    'Generators compute partial public keys and distribute info-theoretic masks to all parties.'))
spacer(4)

body('For each bitmask b, the designated generator gen(b):')
spacer(4)
body('\u2022 Computes partial public key contribution: <b>w^b = InvNTT(A * s1Hat^b) + s2^b</b>')
spacer(4)
body(
    '\u2022 Splits w^b into N info-theoretic masks via splitVectorK:'
)
spacer(4)
body('    \u2013 Sample N-1 uniform random masks r_{b,j} for all j != gen(b)')
spacer(4)
body('    \u2013 Compute residual: r_{b,gen(b)} = w^b - \u2211 other masks (mod q)')
spacer(4)
body('\u2022 Sends r_{b,j} to party j via <b>confidential channel</b>.')
spacer(4)
body('\u2022 Keeps r_{b,gen(b)} locally \u2014 the residual is never transmitted.')

# ── Phase 4 ──
_flush_heading_with(g.StepIndicator(4, 'Phase 4: Aggregate & Finalize',
    'Parties aggregate masks, reconstruct the public key, and verify via test signing.',
    is_last=True))
spacer(4)

body('Each party j:')
spacer(4)
body('\u2022 Computes local aggregate: <b>R_j = \u2211 over all b of r_{b,j}</b> (mod q)')
spacer(4)
body('\u2022 <b>Broadcasts</b> R_j')
spacer(8)
body('<b>Finalization</b> (all parties, deterministic):')
spacer(4)
code('t  = sum_{j=0}^{N-1} R_j  (mod q)    // masks cancel: yields A*s1 + s2\n(t0, t1) = Power2Round(t)\npublicKey = Encode(rho, t1)\ntr = SHAKE-256(publicKey)', lang='')
spacer(4)
body('Each party constructs their <b>ThresholdKeyShare</b> containing: their party id, rho, tr, a locally-generated 32-byte key, and their shares for all bitmasks where their bit is set.')
spacer(8)
info_box(
    'After DKG completes, parties perform a test threshold signing of a known message. If the '
    'resulting signature verifies against the public key, the DKG succeeded. If not, a party '
    'cheated during mask distribution \u2014 restart with a fresh session.',
    title='POST-DKG VERIFICATION'
)

sub_heading('9.5 Mask Cancellation: Why It Works')

body(
    'The correctness of Phase 4 depends on mask cancellation:'
)
spacer(4)
body(
    't = \u2211_j R_j = \u2211_j \u2211_b r_{b,j} = \u2211_b \u2211_j r_{b,j} = \u2211_b w^b '
    '= \u2211_b (A \u00b7 s1^b + s2^b) = A \u00b7 (\u2211_b s1^b) + (\u2211_b s2^b) '
    '= A \u00b7 s1_total + s2_total'
)
spacer(8)
body(
    'The key insight: swapping the order of summation makes the random masks cancel. For each bitmask '
    'b, the N mask pieces r_{b,j} were constructed so that \u2211_j r_{b,j} = w^b. Therefore the '
    'double sum over all j and all b yields the sum of all w^b values, which equals A \u00b7 s1 + s2.'
)

sub_heading('9.6 Complaint and Abort Protocol')

body(
    'The per-bitmask seed design eliminates most complaint scenarios:'
)
spacer(8)

table(
    ['Attack', 'Per-Generator Local', 'Per-Bitmask Seed (PERMAFROST)'],
    [
        ['Biased share', 'Undetectable', 'IMPOSSIBLE (forced by seed)'],
        ['Equivocated share', 'Detected by commitment', 'IMPOSSIBLE (local derivation)'],
        ['Wrong share sent', 'Detected by commitment', 'IMPOSSIBLE (no sending needed)'],
        ['Withheld reveal', 'N/A', 'Detected \u2192 abort + restart'],
        ['Wrong mask pieces', 'Signing fails', 'Detected by test sign \u2192 restart'],
        ['Withheld mask piece', 'Protocol stuck', 'Detected \u2192 abort + restart'],
    ],
    [0.22, 0.35, 0.43],
)

spacer(8)
body(
    'All abort scenarios lead to restart with a new session_id. Per Theorem 5, this is safe \u2014 '
    'session isolation ensures no cross-session information leakage.'
)

sub_heading('9.7 Message Complexity')

body(
    'For a DKG with parameters (T, N), let |B| = C(N, N-T+1) bitmask count and k = N-T+1 holders '
    'per bitmask:'
)
spacer(8)

table(
    ['Phase', 'Broadcasts', 'Private Messages'],
    [
        ['1 (Commit)', 'N messages with hashes', '0'],
        ['2 (Reveal)', 'N messages (rho_i)', '|B| \u00b7 k \u00b7 (k-1) msgs of 32 bytes'],
        ['3 (Mask)', '0', '|B| \u00b7 (N-1) mask pieces (~3 KB each)'],
        ['4 (Aggregate)', 'N messages (R_j)', '0'],
    ],
    [0.20, 0.35, 0.45],
)

spacer(8)
body(
    '<b>Worst case (T=4, N=6):</b> |B|=20, k=3. Phase 2: 120 private messages of 32 bytes = 3.8 KB. '
    'Phase 3: 100 mask pieces of ~3 KB each = ~300 KB. Total: ~304 KB \u2014 well within practical '
    'limits for a one-time DKG ceremony.'
)

sub_heading('9.8 Security Proofs')

body(
    'The following theorems formally establish the security properties of the PERMAFROST dealerless DKG. '
    'These proofs rely on no new cryptographic assumptions beyond what ML-DSA already requires.'
)

sub_sub_heading('Theorem 1: Correctness')

body(
    '<b>Statement.</b> The distributed DKG produces a valid ML-DSA public key (\u03c1, t\u2081), '
    'and the resulting ThresholdKeyShare values are compatible with the existing threshold signing protocol.'
)
spacer(8)
body('<b>Proof.</b>')
spacer(4)
body(
    'The total secret: s\u2081 = \u2211_{b \u2208 B} s\u2081^b, s\u2082 = \u2211_{b \u2208 B} s\u2082^b.'
)
spacer(4)
body(
    'Each (s\u2081^b, s\u2082^b) is derived via deriveUniformLeqEta(seed_b, ...), which produces '
    'polynomials with coefficients in [-\u03b7, \u03b7] \u2014 identical to the key generation method\'s '
    'derivation.'
)
spacer(4)
body(
    'By linearity of matrix multiplication and polynomial addition:'
)
code('''t = A * s1 + s2
  = sum_b (A * s1^b + s2^b)    [linearity]
  = sum_b w^b                   [definition of w^b]
  = sum_b sum_j r_{b,j}         [mask reconstruction: sum_j r_{b,j} = w^b]
  = sum_j sum_b r_{b,j}         [swap finite sums]
  = sum_j R_j                   [definition of R_j]''', lang='')
spacer(4)
body(
    'Mask cancellation holds because \u2211_j r_{b,j} = w^b by construction: N-1 masks are sampled '
    'uniformly, and the residual is computed as w^b minus the sum of the other masks.'
)
spacer(4)
body(
    'Power2Round(t) yields (t\u2080, t\u2081), publicKey = Encode(\u03c1, t\u2081) is a valid FIPS 204 '
    'public key. For signing: the share recovery algorithm (#recoverShare) selects shares by bitmask and '
    'sums them. It depends only on share values and the sharing pattern. Shares from the distributed DKG '
    'are functionally identical to single-device shares. \u220e'
)

sub_sub_heading('Theorem 2: Structural Secrecy')

body(
    '<b>Statement.</b> For every party i, there exists at least one bitmask b* \u2208 B such that '
    'i \u2209 b*. Party i never learns seed_{b*} or (s\u2081^{b*}, s\u2082^{b*}), and therefore '
    'cannot reconstruct (s\u2081, s\u2082).'
)
spacer(8)
body('<b>Proof.</b>')
spacer(4)
body(
    '<i>Existence of b*:</i> Bitmasks have (N-T+1) bits set. The number NOT containing bit i is '
    'C(N-1, N-T+1) &gt; 0 for T \u2265 2. \u2713'
)
spacer(4)
body(
    '<i>Structural separation:</i> seed_{b*} is derived from {r_{i,b*} : i \u2208 b*}. Since '
    'i \u2209 b*, party i:'
)
spacer(4)
body('\u2022 Did not contribute any r_{i,b*} (they are not a holder)')
body('\u2022 Never received any r_{k,b*} (reveals are private to holders of b*)')
body('\u2022 Cannot compute seed_{b*} (missing all inputs except the broadcast commitments, which are SHAKE-256 hashes)')
spacer(4)
body(
    'Therefore party i cannot derive (s\u2081^{b*}, s\u2082^{b*}).'
)
spacer(4)
body(
    '<i>Computational residual:</i> The public transcript reveals only t = A \u00b7 s\u2081 + s\u2082. '
    'Party i can subtract their known shares\' contributions to get A \u00b7 s\u2081^{b*} + s\u2082^{b*} '
    '+ [other unknown terms]. In the best case for the adversary (only one unknown bitmask), this is a '
    'single Module-LWE sample. Recovery requires solving MLWE. \u220e'
)

sub_sub_heading('Theorem 3: Forced Randomness')

body(
    '<b>Statement.</b> If at least one holder of bitmask b is honest, then seed_b is computationally '
    'indistinguishable from uniform, and the derived share (s\u2081^b, s\u2082^b) has the canonical '
    'LeqEta distribution.'
)
spacer(8)
body('<b>Proof.</b>')
spacer(4)
body(
    '<i>Commit-before-reveal prevents adaptive choice:</i> All parties commit to r_{i,b} in Phase 1 '
    'before any reveals in Phase 2. Changing r_{i,b} after committing requires finding a SHAKE-256 '
    'second preimage \u2014 computationally infeasible.'
)
spacer(4)
body(
    '<i>Honest contribution forces uniformity:</i> Let party h be the honest holder. After all '
    'commitments are broadcast, r_{h,b} is uniformly random and independent of all other r_{i,b} '
    'values (which were committed before r_{h,b} was chosen \u2014 the binding property ensures no '
    'party can adapt after committing).'
)
spacer(4)
body(
    'seed_b = SHAKE-256("DKG-BSEED" || sid || encode_u16le(b) || r_{p\u2080,b} || ... || r_{pk,b}, dkLen=64)'
)
spacer(4)
body(
    'In the random oracle model, if r_{h,b} is uniform and independent of the other inputs (given '
    'the binding of their commitments), then seed_b is indistinguishable from uniform.'
)
spacer(4)
body(
    '<i>Deterministic derivation preserves distribution:</i> deriveUniformLeqEta(seed_b, nonce) uses '
    'SHAKE-256 as a PRF to produce coefficients with the uniform LeqEta distribution. If seed_b is '
    'pseudorandom, the output is computationally indistinguishable from the canonical distribution.'
)
spacer(4)
body(
    '<i>No equivocation:</i> All holders independently compute seed_b from the same inputs, arriving '
    'at the same share. There is no "distribution" of shares between holders \u2014 each computes locally. \u220e'
)

sub_sub_heading('Theorem 4: Public-Key Transcript Equivalence')

body(
    '<b>Statement.</b> The public transcript reveals only information equivalent to the standard '
    'ML-DSA public key (\u03c1, t\u2081). No per-bitmask MLWE samples are leaked.'
)
spacer(8)
body('<b>Proof.</b>')
spacer(4)
body('The public transcript consists of:')
body('\u2022 {C_i^\u03c1} \u2014 SHAKE-256 hashes (preimage-resistant)')
body('\u2022 {C_{i,b}} \u2014 SHAKE-256 hashes (preimage-resistant)')
body('\u2022 {\u03c1_i} \u2014 random nonces, aggregate determines \u03c1 (already public)')
body('\u2022 {R_j} \u2014 per-party masked aggregates')
spacer(4)
body(
    '<i>R_j values are statistically uniform:</i> R_j = \u2211_b r_{b,j}. For at least one bitmask b\' '
    'where gen(b\') \u2260 j, the term r_{b\',j} was sampled uniformly by the generator. A sum including '
    'at least one uniform independent term is itself uniform.'
)
spacer(4)
body(
    '<i>Only the sum carries signal:</i> (R\u2080, ..., R_{N-1}) is constrained by \u2211_j R_j = t. '
    'Any strict subset {R_j : j \u2208 S, |S| &lt; N} is independent of individual w^b values. This '
    'is the standard property of additive N-out-of-N secret sharing.'
)
spacer(4)
body(
    'The extractable information equals one MLWE sample (A, t) \u2014 matching standard ML-DSA key '
    'generation exactly. \u220e'
)

sub_sub_heading('Theorem 5: Abort Safety and Session Isolation')

body(
    '<b>Statement.</b> Abort at any phase is safe. Restarting with a fresh session_id produces an '
    'independent DKG instance. No cross-session information leakage occurs.'
)
spacer(8)
body('<b>Proof.</b>')
spacer(4)
body(
    '<i>Domain separation:</i> session_id is incorporated into every hash and commitment. '
    'Cross-session replay requires a SHAKE-256 collision.'
)
spacer(4)
body(
    '<i>Phase 1 abort:</i> Only hash commitments have been broadcast \u2014 no secret material exposed.'
)
spacer(4)
body(
    '<i>Phase 2 abort:</i> Revealed \u03c1_i are non-sensitive random nonces. Revealed r_{i,b} values '
    '(sent to fellow holders) belong to an aborted session\'s seed. The new session samples fresh '
    'r_{i,b}\' values from independent randomness. Even if an adversary learns some r_{i,b} from the '
    'old session, these are uncorrelated with the new session\'s values.'
)
spacer(4)
body(
    '<i>Phase 3 abort:</i> Mask pieces r_{b,j} are uniform random (statistically independent of '
    'secrets without the full set).'
)
spacer(4)
body('<i>Phase 4 abort:</i> R_j values are uniform (Theorem 4). \u220e')

sub_sub_heading('Theorem 6: LeqEta Bias Non-Exploitability')

body(
    '<b>Statement.</b> In the edge case where ALL holders of some bitmask b are malicious (possible '
    'when N &lt; 2T - 1), they can bias seed_b and hence (s\u2081^b, s\u2082^b). This does not '
    'compromise: (a) signature unforgeability, (b) secret recovery hardness, or (c) overall MLWE security.'
)
spacer(8)
body('<b>Proof.</b>')
spacer(4)
body(
    'Even with adversarial choice of seed_b, the derived shares satisfy coeff \u2208 [-\u03b7, \u03b7] '
    '(enforced by deriveUniformLeqEta\'s rejection sampling, which always produces valid LeqEta '
    'coefficients regardless of seed \u2014 there is no seed that produces out-of-range coefficients).'
)
spacer(4)
body(
    '<i>(a) Unforgeability:</i> Rejection sampling bounds (r, r\', K_iter) assume worst-case [-\u03b7, \u03b7] '
    'norms. Biased distribution can only reduce norms below worst case, improving (not degrading) '
    'rejection sampling success rate. Unforgeability follows from the same Module-SIS/LWE reduction.'
)
spacer(4)
body(
    '<i>(b) Secret recovery:</i> The adversary\'s own biased shares don\'t help recover non-held shares. '
    'Non-held shares are generated by subgroups containing at least one honest party (different bitmask). '
    'The residual is still MLWE-hard.'
)
spacer(4)
body(
    '<i>(c) MLWE hardness:</i> The public key t = A \u00b7 \u2211_b s\u2081^b + \u2211_b s\u2082^b '
    'has L\u221e norm at most |B| \u00b7 \u03b7 per coefficient. MLWE hardness depends on the norm '
    'bound, not the distribution within it. \u220e'
)

spacer(8)
info_box(
    'No new cryptographic assumption beyond what ML-DSA already requires. The DKG uses only: '
    'SHAKE-256 collision/preimage resistance (ML-DSA requires this), SHAKE-256 as PRF/XOF in the '
    'random oracle model (ML-DSA requires this), Module-LWE hardness (ML-DSA requires this), and '
    'authenticated confidential channels (standard for all DKGs).',
    title='ASSUMPTION SUMMARY'
)


# ======================================================================
# 10. HYPERBALL SAMPLING
# ======================================================================
section_heading('10. Hyperball Sampling')

sub_heading('10.1 Motivation')

body(
    'In standard ML-DSA, the masking vector y is sampled uniformly from [-\u03b3\u2081+1, \u03b3\u2081]^{N\u00b7L}. '
    'This works for single-signer because the signer knows the full secret and can perform rejection '
    'sampling locally. In threshold ML-DSA, each party independently samples a "partial masking" vector. '
    'These must: (1) sum to something that looks like a valid masking vector, (2) not leak information '
    'about individual parties\' secrets, and (3) enable efficient rejection sampling.'
)
spacer(8)
body(
    'The hyperball construction achieves this by sampling from a continuous distribution on a '
    'high-dimensional sphere, then rounding to integers.'
)

sub_heading('10.2 The sampleHyperball Algorithm')

body(
    '<b>Input:</b> radius r\', scaling factor \u03bd, dimensions (K, L), seed rhop (64 bytes), nonce.'
)
body(
    '<b>Output:</b> Float64Array of dimension N\u00b7(K+L).'
)
spacer(8)
body(
    'The algorithm proceeds in three steps:'
)
spacer(4)
body(
    '1. Initialize SHAKE-256 with domain separator: H = SHAKE-256(\'H\' || rhop || nonce_le16).'
)
body(
    '2. Generate dim+2 random floats via Box-Muller pairs (need even count). For each pair (f1, f2) of '
    'uniform random floats: z1 = \u221a(-2\u00b7ln(f1)) \u00b7 cos(2\u03c0\u00b7f2), '
    'z2 = \u221a(-2\u00b7ln(f1)) \u00b7 sin(2\u03c0\u00b7f2). Accumulate L2 norm: sq += z1\u00b2 + z2\u00b2. '
    'Scale first N\u00b7L components by \u03bd (=3.0).'
)
body(
    '3. Normalize to sphere of radius r\': factor = r\' / \u221a(sq), result[i] = samples[i] \u00d7 factor.'
)

sub_heading('10.3 Box-Muller Transform')

body(
    'The Box-Muller transform converts two independent uniform random variables U\u2081, U\u2082 '
    '\u2208 (0, 1) into two independent standard normal variables:'
)
spacer(4)
body(
    'Z\u2081 = \u221a(-2 ln U\u2081) \u00b7 cos(2\u03c0 U\u2082), '
    'Z\u2082 = \u221a(-2 ln U\u2081) \u00b7 sin(2\u03c0 U\u2082)'
)
spacer(8)
body(
    'This works because the projection of a multivariate standard normal onto the unit sphere is '
    'uniformly distributed on that sphere (a well-known result from spherical distribution theory). '
    'The hyperball construction generates dim+2 standard normal samples and normalizes their L2 norm '
    'to radius r\'.'
)

sub_heading('10.4 BigInt Precision for Uniform Floats')

body(
    'Converting 64-bit random bytes to uniform floats in [0, 1) requires care. The naive approach '
    '(Go: float64(uint64) / (1 &lt;&lt; 64)) double-rounds because uint64 values above 2\u2075\u00b3 '
    'cannot be exactly represented as float64.'
)
spacer(8)

code('''// Extract exactly 53 bits of precision
const u: bigint = dataView.getBigUint64(offset, true);
const f: number = Number(u >> 11n) * TWO_NEG_53;
// TWO_NEG_53 = 2^(-53) = 1.1102230246251565e-16 (exact)''')

spacer(8)
body(
    'Shifting right by 11 bits extracts the top 53 bits of the 64-bit value. Since '
    'Number.MAX_SAFE_INTEGER = 2\u2075\u00b3 - 1, the result of Number(u &gt;&gt; 11n) is always '
    'exactly representable. Multiplying by 2^(-53) gives a uniform value in [0, 1 - 2^(-53)].'
)

sub_heading('10.5 The C1 Fix: Avoiding log(0)')

body(
    'Box-Muller requires ln(U\u2081), which is -\u221e when U\u2081 = 0. The probability of U\u2081 = 0 '
    'is 2^(-53). The fix:'
)
spacer(4)

code('''const f1 = f1Raw === 0 ? Number.MIN_VALUE : f1Raw;
// MIN_VALUE ~ 5e-324, gives sqrt(-2*ln(MIN_VALUE)) ~ 38.6
// This sample will be rejected by excess check''')

spacer(8)
body(
    'Number.MIN_VALUE \u2248 5 \u00d7 10^(-324) is the smallest positive denormalized float64. '
    'Using it instead of 0 gives a large but finite value that will almost certainly be rejected '
    'by the excess check, not affecting the distribution meaningfully.'
)


# ======================================================================
# 11. SHARE RECOVERY
# ======================================================================
section_heading('11. Share Recovery')

body(
    'Given T active parties out of N total, each party must reconstruct their combined secret share '
    '(s1Hat, s2Hat) for the specific active set. The key generation distributes shares indexed by '
    'honest-signer bitmasks. Share recovery maps the current active set to the appropriate combination '
    'of stored shares.'
)

sub_heading('11.1 Sharing Patterns')

body(
    'Sharing patterns are precomputed by a max-flow optimal assignment algorithm and stored as lookup '
    'tables indexed by (T, N). Each pattern[i] lists the bitmasks that party i must sum to reconstruct '
    'their share.'
)
spacer(8)
body(
    '<b>Example (T=2, N=3):</b> pattern = [[3, 5], [6]]. Party 0 sums shares with bitmasks '
    '3 (=0b011) and 5 (=0b101). Party 1 sums share with bitmask 6 (=0b110).'
)

sub_heading('11.2 Permutation-Based Bitmask Translation')

body(
    'Sharing patterns are defined for a canonical ordering where the first T parties are active. '
    'When the actual active set differs, a permutation translates bitmask indices:'
)
spacer(8)

code('''// Build permutation: active -> 0..T-1, inactive -> T..N-1
const perm = new Uint8Array(N);
let i1 = 0, i2 = T;
for (let j = 0; j < N; j++) {
  if ((act & (1 << j)) !== 0) perm[i1++] = j;
  else perm[i2++] = j;
}

// Translate bitmask through permutation
let u_ = 0;
for (let i = 0; i < N; i++) {
  if ((u & (1 << i)) !== 0) u_ |= (1 << perm[i]);
}
const s = share.shares.get(u_);''')

sub_heading('11.3 Base Case: T = N')

body(
    'When T = N (all parties required), each party has exactly one share corresponding to the single '
    'C(N, 1) = N subset of size 1. No permutation is needed \u2014 each party returns their single '
    'stored share directly.'
)

sub_heading('11.4 Share Accumulation')

body(
    'After translation, the party sums all assigned shares: for each bitmask u in the sharing pattern, '
    'translate to actual bitmask u\', look up the stored share, and accumulate via polynomial addition '
    'mod q. The result (s1Hat, s2Hat) is this party\'s additive share of the full secret in NTT domain.'
)


# ======================================================================
# 12. THE 3-ROUND DISTRIBUTED SIGNING PROTOCOL
# ======================================================================
section_heading('12. The 3-Round Distributed Signing Protocol')

body(
    'The distributed signing protocol is PERMAFROST\'s core contribution: any T parties independently '
    'generate their own randomness on their own machines, exchange only commitments and responses, '
    'and produce a single standard FIPS 204 signature. No party\'s secret ever leaves their device.'
)
spacer(8)

table(
    ['Round', 'Communication', 'Purpose', 'Data Size'],
    [
        ['Round 1', 'Broadcast 32-byte hash', 'Commit to randomness', '32 bytes'],
        ['Round 2', 'Broadcast packed w vectors', 'Reveal commitment', 'K_iter \u00d7 K \u00d7 736 bytes'],
        ['Round 3', 'Broadcast packed z vectors', 'Partial response', 'K_iter \u00d7 L \u00d7 736 bytes'],
        ['Combine', 'None (local computation)', 'Produce FIPS 204 signature', '0 bytes'],
    ],
    [0.15, 0.30, 0.30, 0.25],
)

sub_heading('12.1 Round 1: Commitment')

_flush_heading_with(g.StepIndicator(1, 'Round 1: Commitment',
    'Each party independently generates randomness, samples hyperball points, and broadcasts a commitment hash.'))
spacer(4)

body('Each party independently:')
spacer(4)
body('<b>1.</b> Generate randomness: <b>rhop</b> = random 64 bytes')
spacer(4)
body('<b>2.</b> Sample K_iter hyperball points: stw[iter] = sampleHyperball(r\', \u03bd, K, L, rhop, nonce)')
spacer(4)
body('<b>3.</b> Round to integer vectors: (y, e) = fvecRound(stw)')
spacer(4)
body('<b>4.</b> Compute commitment: w = A\u00b7NTT(y) + e')
spacer(4)
body('<b>5.</b> Pack commitments into bytes')
spacer(4)
body('<b>6.</b> Hash commitment:')
code('commitmentHash = SHAKE-256(tr || partyId || packedW)  // 32 bytes', lang='')
spacer(8)
body('<b>Output:</b> {commitmentHash (32 bytes), state}. Broadcast hash to all parties.')

spacer(8)
info_box(
    'Without commit-then-reveal, a malicious party could see others\' commitments and choose their '
    'own adaptively to manipulate the combined commitment. The hash commitment prevents this: all '
    'parties commit before any reveals.',
    title='WHY COMMIT-THEN-REVEAL?'
)

sub_heading('12.2 Round 2: Reveal')

_flush_heading_with(g.StepIndicator(2, 'Round 2: Reveal',
    'After receiving all T commitment hashes, each party validates, stores hashes, and reveals their commitment.'))
spacer(4)

body('After receiving all T commitment hashes, each party:')
spacer(4)
body('<b>1.</b> Validate: correct number of hashes, no duplicate party IDs.')
spacer(4)
body('<b>2.</b> Store hashes: save copies for verification in Round 3.')
spacer(4)
body('<b>3.</b> Compute message digest:')
code('\u03bc = SHAKE-256(tr || message)  // 64 bytes', lang='')
spacer(4)
body('<b>4.</b> Reveal commitment: return packed w data from Round 1.')
spacer(8)
body('<b>Output:</b> {commitment (packed bytes), state}. Broadcast commitment to all parties.')

sub_heading('12.3 Round 3: Partial Response')

_flush_heading_with(g.StepIndicator(3, 'Round 3: Partial Response',
    'After receiving all reveals, each party verifies commitments, recovers shares, and computes their partial signature.',
    is_last=True))
spacer(4)

body('After receiving all T commitment reveals, each party:')
spacer(4)
body('<b>1.</b> <b>Verify</b> commitments against stored hashes (constant-time comparison). '
    '<b>Abort</b> if any mismatch detected.')
spacer(4)
body('<b>2.</b> Unpack and aggregate commitments: wfinal = \u2211 of all parties\' w vectors.')
spacer(4)
body('<b>3.</b> Recover combined secret share: (s1Hat, s2Hat) = recoverShare(share, activePartyIds).')
spacer(4)
body('<b>4.</b> For each iteration: compute challenge c, then cs = c\u00b7s, zf = cs + stw, check excess. '
    'Apply H1 fix: <b>always</b> execute fvecRound regardless of excess (see Section 12.4).')
spacer(4)
body('<b>5.</b> Pack and return partial z response.')
spacer(8)
body('<b>Output:</b> packed partial response. Broadcast to all parties.')

sub_heading('12.4 The H1 Timing Fix')

body(
    'The excess check fvecExcess(zf, r, \u03bd) reveals whether the current iteration was accepted or '
    'rejected. If fvecRound() is only called on accepted iterations, the execution time correlates with '
    'the rejection pattern, which correlates with the secret key.'
)
spacer(8)

code('''const excess = fvecExcess(zf, params.r, params.nu, K, L);
const { z } = fvecRound(zf, K, L);  // ALWAYS executed (H1 fix)

if (excess) {
  zs.push(zeroVector);  // Use zero, but fvecRound already ran
} else {
  zs.push(z);           // Accept this iteration
}''')

spacer(8)

critical_box(
    'Without the H1 fix, the execution time of fvecRound (which involves Math.round on every '
    'coefficient) is secret-dependent. This timing leak could allow an attacker to determine the '
    'rejection pattern across multiple signing sessions, gradually extracting information about '
    'the secret key. Always executing fvecRound ensures constant execution time.',
    title='H1 TIMING LEAK'
)


# ======================================================================
# 13. COMBINE: SIGNATURE FINALIZATION
# ======================================================================
section_heading('13. Combine: Signature Finalization')

body(
    'The combine step produces the final standard FIPS 204 signature from the aggregated data. '
    'It requires only the threshold public key, the message, all parties\' commitments, and all '
    'parties\' responses. <b>It does NOT require any secret key material</b> \u2014 anyone with '
    'the public key can perform this step.'
)

sub_heading('13.1 The Combine Algorithm')

body(
    'For each iteration iter = 0 to K_iter-1:'
)
spacer(4)
body(
    '1. Aggregate commitments: wfinal[iter][j] = \u2211 allWs[party][iter][j] mod q.'
)
body(
    '2. Aggregate responses: zfinal[iter][j] = \u2211 allZs[party][iter][j] mod q.'
)
body(
    '3. Check ||zfinal||\u221e &lt; \u03b3\u2081 - \u03b2. Skip if fails.'
)
body(
    '4. Decompose: (w0, w1) = Decompose(wfinal[iter]).'
)
body(
    '5. Recompute challenge: c\u0303 = SHAKE-256(\u03bc || W1Encode(w1)), c = SampleInBall(c\u0303).'
)
body(
    '6. Compute Az in NTT domain: Az[i] = \u2211_j A[i][j] \u00b7 NTT(z[j]).'
)
body(
    '7. Compute Az - 2^d \u00b7 c \u00b7 t\u2081: ct12d[i] = NTT(c) \u00b7 NTT(t\u2081[i] &lt;&lt; d).'
)
body(
    '8. Compute f = InvNTT(Az - ct12d) - wfinal. Check ||f||\u221e &lt; \u03b3\u2082.'
)
body(
    '9. Compute hint: h = MakeHint(w0 + f, w1). Check weight(h) \u2264 \u03c9.'
)
body(
    '10. Success! Encode signature: \u03c3 = sigCoder.encode([c\u0303, z, h]). Return \u03c3.'
)

sub_heading('13.2 Why This Produces Valid FIPS 204 Signatures')

body(
    'The key mathematical identity that makes threshold signing work:'
)
spacer(4)
body(
    'Az - c \u00b7 t\u2081 \u00b7 2^d = A \u00b7 (\u2211 y_i + c \u00b7 \u2211 s\u2081_i) '
    '- c \u00b7 (A \u00b7 \u2211 s\u2081_i + \u2211 s\u2082_i - \u2211 t\u2080_i) \u00b7 2^d '
    '\u2248 A \u00b7 \u2211 y_i + \u2211 e_i + c \u00b7 \u2211 s\u2082_i = wfinal + c \u00b7 s\u2082'
)
spacer(8)
body(
    'The "approximately" comes from rounding errors in fvecRound. The hint h corrects for these '
    'small differences, exactly as in standard ML-DSA. The verifier computes w\'_approx = Az - c \u00b7 t\u2081 \u00b7 2^d, '
    'applies UseHint(h, w\'_approx) to get w\'\u2081, and checks SHAKE-256(\u03bc || W1Encode(w\'\u2081)) = c\u0303. '
    'This is identical to standard FIPS 204 verification.'
)

info_box(
    'Protection of t1: When computing NTT(polyShiftl(t1[i])), the polyShiftl operation modifies '
    'the polynomial in-place (left-shifts by d=13 bits). To prevent corrupting the decoded public '
    'key data, we operate on a copy: t1[i].slice(). This defensive copy is essential for correctness.',
    title='IMPLEMENTATION NOTE'
)


# ======================================================================
# 14. POLYNOMIAL PACKING
# ======================================================================
section_heading('14. Polynomial Packing: 23-Bit Encoding')

body(
    'The distributed protocol needs to transmit full R_q polynomials (coefficients in [0, q)) '
    'between parties. Since q = 8,380,417 &lt; 2\u00b2\u00b3, each coefficient requires exactly 23 bits.'
)

sub_heading('14.1 Encoding: polyPackW')

body(
    'Input: Int32Array[256] with values in [0, 2\u00b2\u00b3). Output: Uint8Array[736] (256 \u00d7 23 / 8 = 736 bytes).'
)
spacer(4)

code('''// Bit-packing algorithm
v = 0, j = 0
for each coefficient p[i]:
  v |= (p[i] & 0x7FFFFF) << j     // append 23 bits
  j += 23
  while j >= 8:                     // flush complete bytes
    buf[k++] = v & 0xFF
    v >>>= 8
    j -= 8''', lang='typescript')

sub_heading('14.2 Decoding: polyUnpackW (with M7 Validation Fix)')

code('''// Bit-unpacking with M7 bounds check
v = 0, j = 0
for each output coefficient:
  while j < 23:                     // need 23 bits
    v += buf[k++] << j
    j += 8
  coeff = v & ((1 << 23) - 1)       // extract 23 bits
  if (coeff >= Q) throw Error        // M7 FIX: validate!
  v >>>= 23
  j -= 23''', lang='typescript')

spacer(8)

warning_box(
    'M7 Fix: The unpacking MUST validate that each coefficient is in [0, q). This prevents an '
    'adversary in a distributed protocol from injecting malformed polynomials with coefficients '
    '>= q, which could cause undefined behavior in ring arithmetic.',
    title='M7 VALIDATION FIX'
)

sub_heading('14.3 Bit Safety Analysis')

body(
    'All intermediate values in the packing/unpacking fit within 32-bit integers. Maximum accumulator '
    'value during packing: v = coeff &lt;&lt; j where coeff &lt; 2\u00b2\u00b3 and j &lt; 8, so '
    'v &lt; 2\u00b3\u00b9. Maximum accumulator during unpacking: v = byte &lt;&lt; j where '
    'byte &lt; 2\u2078 and j &lt; 23, so v &lt; 2\u00b3\u00b9. No 53-bit overflow is possible.'
)
spacer(8)
body(
    '<b>Communication sizes:</b> Commitment = K_iter \u00d7 K \u00d7 736 bytes (e.g., 2 \u00d7 4 \u00d7 736 '
    '= 5,888 bytes for ML-DSA-44, 2-of-2). Response = K_iter \u00d7 L \u00d7 736 bytes.'
)


# ======================================================================
# 15. PARAMETER TABLES
# ======================================================================
section_heading('15. Parameter Tables')

sub_heading('15.1 ML-DSA-44 (K=4, L=4, NIST Level 2)')

table(
    ['T\\N', '2', '3', '4', '5', '6'],
    [
        ['2', 'K=2', 'K=3', 'K=3', 'K=3', 'K=4'],
        ['3', '\u2014', 'K=4', 'K=7', 'K=14', 'K=19'],
        ['4', '\u2014', '\u2014', 'K=8', 'K=30', 'K=74'],
        ['5', '\u2014', '\u2014', '\u2014', 'K=16', 'K=100'],
        ['6', '\u2014', '\u2014', '\u2014', '\u2014', 'K=37'],
    ],
    [0.12, 0.18, 0.18, 0.18, 0.18, 0.16],
)

spacer(8)
body(
    '<b>Full parameters for ML-DSA-44 (selected configurations):</b>'
)
spacer(4)

table(
    ['(T,N)', 'K_iter', 'r', 'r\'', '\u03bd'],
    [
        ['(2,2)', '2', '252,778', '252,833', '3.0'],
        ['(2,3)', '3', '310,060', '310,138', '3.0'],
        ['(3,3)', '4', '246,490', '246,546', '3.0'],
        ['(3,5)', '14', '282,800', '282,912', '3.0'],
        ['(4,5)', '30', '259,427', '259,526', '3.0'],
        ['(4,6)', '74', '268,705', '268,831', '3.0'],
        ['(5,6)', '100', '250,590', '250,686', '3.0'],
        ['(6,6)', '37', '219,245', '219,301', '3.0'],
    ],
    [0.15, 0.15, 0.25, 0.25, 0.20],
)

sub_heading('15.2 ML-DSA-65 (K=6, L=5, NIST Level 3)')

table(
    ['(T,N)', 'K_iter', 'r', 'r\''],
    [
        ['(2,2)', '2', '344,000', '344,080'],
        ['(2,3)', '3', '421,700', '421,810'],
        ['(3,3)', '4', '335,200', '335,290'],
        ['(3,5)', '14', '384,600', '384,750'],
        ['(5,6)', '100', '340,700', '340,830'],
        ['(6,6)', '37', '298,000', '298,080'],
    ],
    [0.20, 0.20, 0.30, 0.30],
)

sub_heading('15.3 ML-DSA-87 (K=8, L=7, NIST Level 5)')

table(
    ['(T,N)', 'K_iter', 'r', 'r\''],
    [
        ['(2,2)', '2', '442,000', '442,100'],
        ['(2,3)', '3', '541,600', '541,740'],
        ['(3,3)', '4', '430,600', '430,710'],
        ['(3,5)', '14', '494,200', '494,400'],
        ['(5,6)', '100', '437,400', '437,570'],
        ['(6,6)', '37', '382,800', '382,910'],
    ],
    [0.20, 0.20, 0.30, 0.30],
)

sub_heading('15.4 Why N \u2264 6')

body(
    'N is capped at 6 for mathematical and practical reasons:'
)
spacer(4)
body(
    '<b>1. Combinatorial explosion:</b> C(N, N-T+1) subsets. N=6: up to 20 subsets. N=10: up to 252 subsets.'
)
body(
    '<b>2. K_iter growth:</b> For (T=5, N=6), K_iter = 100, meaning each signing round requires '
    '100 parallel attempts. Communication: 100 \u00d7 4 \u00d7 736 = 294 KB per party per round.'
)
body(
    '<b>3. Parameter table size:</b> Each (T,N) needs empirically optimized (K_iter, r, r\') values.'
)
body(
    '<b>4. Share storage:</b> Each party stores shares for all subsets they belong to. More subsets = more key storage.'
)
spacer(8)
body(
    'The signature size NEVER changes \u2014 it\'s always standard FIPS 204. The extra communication '
    'during signing is off-chain between parties. Beyond N=6, this communication becomes impractical.'
)


# ======================================================================
# 16. SECURITY ANALYSIS AND HARDENING
# ======================================================================
section_heading('16. Security Analysis and Hardening')

body(
    'The Go reference implementation has known vulnerabilities identified in its audit report. '
    'PERMAFROST addresses all five findings and adds additional hardening.'
)
spacer(8)

g.add_severity_badges(story, cw, critical=2, high=2, medium=1, low=0, info=0)
spacer(12)

sub_heading('16.1 C1 (Critical): Box-Muller NaN/Infinity from log(0)')

body(
    '<b>Vulnerability:</b> When U\u2081 = 0 (probability 2^(-53)), Math.log(0) = -Infinity, '
    'causing NaN propagation through all subsequent arithmetic.'
)
spacer(4)
body(
    '<b>Fix:</b> Clamp to Number.MIN_VALUE:'
)

code('''const f1 = f1Raw === 0 ? Number.MIN_VALUE : f1Raw;
// MIN_VALUE ~ 5e-324, gives sqrt(-2*ln(MIN_VALUE)) ~ 38.6''')

sub_heading('16.2 C8 (Critical): No Input Validation')

body(
    '<b>Vulnerability:</b> Passing wrong-length or undefined values to sign() could cause silent '
    'misbehavior \u2014 wrong polynomial sizes, buffer overflows, or silently incorrect signatures.'
)
spacer(4)
body('<b>Fix:</b> abytes() length checks on all inputs:')

code('''abytes(publicKey, p.publicCoder.bytesLen, 'publicKey');
abytes(msg);  // validates it's a Uint8Array''')

sub_heading('16.3 H1 (High): Timing Leak from Rejection Pattern')

body(
    '<b>Vulnerability:</b> The accept/reject decision depends on the secret key. If fvecRound() is '
    'only called on accepted iterations, execution time reveals the rejection pattern.'
)
spacer(4)
body('<b>Fix:</b> Always execute fvecRound() regardless of the excess check result (see Section 12.4).')

sub_heading('16.4 H6 (High): No Zeroization of Secret Material')

body(
    '<b>Vulnerability:</b> Secret shares, intermediate products (c\u00b7s\u2081, c\u00b7s\u2082), '
    'and the message digest \u03bc remain in memory after use.'
)
spacer(4)
body('<b>Fix:</b> Explicit zeroization on both success and failure paths:')

code('''// After each iteration:
csVec.fill(0); zf.fill(0); cleanBytes(cs1, cs2);

// After all iterations:
cleanBytes(s1Hat, s2Hat);  // recovered share

// In sign() - even on failure:
try { ... } finally { mu.fill(0); }''')

sub_heading('16.5 M7 (Medium): No Coefficient Validation on Unpack')

body(
    '<b>Vulnerability:</b> In distributed protocol, a malicious party could send polynomials with '
    'coefficients \u2265 q, leading to undefined behavior in ring arithmetic.'
)
spacer(4)
body('<b>Fix:</b> Bounds check in polyUnpackW (see Section 14.2).')

sub_heading('16.6 Additional Hardening')

body(
    '<b>Duplicate Share ID Validation:</b> Prevents incorrect bitmask construction from duplicate IDs.'
)
spacer(4)
body(
    '<b>Commitment Hash Verification (Constant-Time):</b> Uses bitwise OR of XOR differences to '
    'prevent timing-based attacks in Round 3.'
)
spacer(4)
body(
    '<b>State Destruction Classes:</b> Round1State and Round2State use #private fields and provide '
    'destroy() methods that zero all sensitive data.'
)
spacer(4)
body(
    '<b>Failure-Path Cleanup:</b> Message digest \u03bc is zeroed even when all 500 signing '
    'attempts are exhausted.'
)


# ======================================================================
# 17. FRONTEND INTEGRATION
# ======================================================================
section_heading('17. Frontend Integration: Communication Layer')

body(
    'The PERMAFROST protocol requires T wallets to exchange messages during the 3-round signing '
    'process. This section describes the recommended communication architecture for wallet-to-wallet '
    'coordination.'
)

sub_heading('17.1 The Communication Problem')

body(
    'N wallets need to exchange messages securely for both DKG (4 phases, one-time) and signing '
    '(3 rounds, per transaction). Requirements: authenticated channels, message ordering, low latency, '
    'and end-to-end encryption.'
)

sub_heading('17.2 Option 1: WebRTC DataChannels')

body(
    'WebRTC provides peer-to-peer encrypted communication via DataChannels, with a signaling server '
    'only for connection setup. Pros: true P2P, built-in DTLS encryption. Cons: complex NAT traversal, '
    'TURN server fallback, connection setup latency.'
)

sub_heading('17.3 Recommended: Encrypted Mailbox over WebSocket')

body(
    'The recommended approach uses a WebSocket-based mailbox server where parties deposit and retrieve '
    'encrypted messages. Each party connects to the mailbox, encrypts messages using hybrid '
    'X25519 + ML-KEM-768 double encryption (Section 17.4), and polls for incoming messages.'
)
spacer(8)
body(
    '<b>Why WebSocket mailbox wins:</b> Simple deployment (single server), no NAT traversal issues, '
    'works through firewalls, asynchronous message delivery (parties don\'t need to be online '
    'simultaneously), and the mailbox server sees only encrypted ciphertext.'
)

sub_heading('17.4 E2E Encryption: Hybrid X25519 + ML-KEM (Dual System)')

body(
    'The DKG transport layer carries bitmask seed reveals and mask pieces. An attacker who records '
    'this traffic and later breaks the transport encryption can reconstruct every bitmask share and '
    'recover the full secret key. This is a textbook "harvest now, decrypt later" attack. The transport '
    'layer must therefore be resistant to both classical and quantum adversaries.'
)
spacer(8)
body(
    'PERMAFROST mandates <b>hybrid (double) encryption</b> for all DKG traffic: X25519 ECDH combined '
    'with ML-KEM-768 (FIPS 203) key encapsulation. The shared secret is derived from both key agreements, so an '
    'attacker must break BOTH to decrypt the traffic. This follows the same principle deployed in '
    'production by Google (CECPQ1/CECPQ2), Cloudflare, and Chrome \u2014 now approaching 50% of all '
    'TLS connections.'
)
spacer(8)
body(
    '<b>Why hybrid, not standalone ML-KEM?</b> Daniel J. Bernstein documents extensively how post-quantum '
    'cryptosystems can fail unexpectedly. SIKE was applied to millions of real connections in 2019 via '
    'CECPQ2b; it was publicly broken in 2022. The ONLY reason user data wasn\'t immediately exposed is '
    'that CECPQ2b encrypted with SIKE AND with ECC, not just SIKE. ML-KEM\'s reference implementation '
    'required two rounds of security patches for timing leaks (KyberSlash, late 2023) and a third patch '
    'in mid-2024. Standalone post-quantum is driving without a seatbelt.'
)
spacer(8)
body(
    '<b>Protocol:</b> Each party generates an ephemeral X25519 keypair AND an ephemeral ML-KEM-768 '
    'keypair per DKG session. For each pair of parties (i, j):'
)
spacer(4)
body('\u2022 Party i performs X25519 ECDH with party j\'s X25519 public key \u2192 shared_ecdh (32 bytes)')
body('\u2022 Party i encapsulates to party j\'s ML-KEM-768 encapsulation key \u2192 shared_kem (32 bytes)')
body('\u2022 Combined key: SHAKE-256("PERMAFROST-TRANSPORT" || shared_ecdh || shared_kem, dkLen=32)')
body('\u2022 The combined key is used as the AES-256-GCM key for encrypting round messages between that pair')
spacer(8)
body(
    '<b>Security properties:</b> If ML-KEM breaks (like SIKE did), X25519 still protects the traffic '
    'against classical adversaries. If X25519 breaks (quantum computer), ML-KEM-768 still provides '
    '192-bit post-quantum security. An attacker must break both simultaneously to recover DKG secrets. '
    'Per-session ephemeral keys provide forward secrecy \u2014 compromising one ceremony reveals nothing '
    'about past or future DKG sessions.'
)
spacer(8)
warning_box(
    'Using standalone pre-quantum (X25519 only) OR standalone post-quantum (ML-KEM only) for DKG '
    'transport is insufficient. Pre-quantum alone falls to harvest-now-decrypt-later. Post-quantum alone '
    'risks a SIKE-class catastrophic break with no fallback. The hybrid approach ensures that the '
    'security of the transport layer is the STRONGER of the two components, not the weaker.',
    title='HYBRID TRANSPORT IS MANDATORY'
)

spacer(8)
info_box(
    'A live demo of the PERMAFROST communication layer is available at:\n'
    'https://ipfs.opnet.org/ipfs/bafybeiejz5fc44scvp5qbgz4zzeg3jieccd5t7dwr6o3dqqhbk54czlhia/',
    title='LIVE DEMO'
)


# ======================================================================
# 18. FLOAT64 PRECISION ANALYSIS
# ======================================================================
section_heading('18. Float64 Precision Analysis')

sub_heading('18.1 Where Float64 is Used')

body(
    'Float64 (IEEE 754 double precision) is used exclusively in hyperball sampling and the FVec '
    'operations: sampleHyperball (Box-Muller), fvecFrom (Int32 \u2192 Float64 conversion), '
    'fvecAdd (vector addition), fvecExcess (weighted L2 norm), and fvecRound (Float64 \u2192 Int32 '
    'rounding).'
)

sub_heading('18.2 Ring Arithmetic: Always Int32')

body(
    'All ring operations (polyAdd, polySub, MultiplyNTTs, NTT encode/decode) use Int32Array and '
    'stay within safe integer range. Maximum coefficient: q-1 = 8,380,416 (23 bits). Maximum product: '
    '(q-1)\u00b2 \u2248 7.02 \u00d7 10\u00b9\u00b3 (47 bits) \u2014 within 53-bit safe range. '
    'All cryptographic ring arithmetic is exact.'
)

sub_heading('18.3 Platform Dependence of Transcendental Functions')

body(
    'Math.sqrt, Math.cos, Math.sin, Math.log may differ by 1 ULP across platforms. This means: '
    'cross-platform deterministic signing is NOT guaranteed, but each platform independently produces '
    'valid signatures. The protocol\'s security depends on statistical properties, not determinism.'
)

sub_heading('18.4 fvecRound Precision')

body(
    'The rounding step: u = Math.round(v) | 0. Since Float64 values are bounded by \u00b14,190,208 '
    'and hyperball radii are ~250,000-550,000, rounded values fit in int32. The | 0 truncation is safe.'
)


# ======================================================================
# 19. ARCHITECTURE AND IMPLEMENTATION
# ======================================================================
section_heading('19. Architecture and Implementation')

sub_heading('19.1 Module Structure')

body(
    'The reference implementation is available at '
    '<b>github.com/btc-vision/noble-post-quantum</b>, a fork of Paul Miller\'s noble-post-quantum '
    'library extended with threshold ML-DSA and dealerless DKG. The implementation consists of four '
    'key modules:'
)
spacer(4)
body(
    '<b>_crystals.ts:</b> NTT, XOF (SHAKE-128/256), core finite field operations.'
)
body(
    '<b>ml-dsa-primitives.ts:</b> Ring arithmetic, coders, sampling, decomposition functions. '
    'The createMLDSAPrimitives() factory extracts shared functionality for reuse.'
)
body(
    '<b>ml-dsa.ts:</b> Standard FIPS 204 implementation (keygen/sign/verify).'
)
body(
    '<b>threshold-ml-dsa.ts:</b> ThresholdMLDSA class with the complete distributed protocol.'
)

sub_heading('19.2 Class Design: ThresholdMLDSA')

code('''class ThresholdMLDSA {
  static readonly MAX_PARTIES = 6;
  static create(securityLevel, T, N): ThresholdMLDSA;
  static getParams(T, N, securityLevel): ThresholdParams;

  // Key generation
  keygen(seed?): ThresholdKeygenResult;

  // Local convenience
  sign(msg, publicKey, shares, opts?): Uint8Array;

  // Distributed protocol
  round1(share, opts?): Round1Result;
  round2(share, ids, msg, hashes, state, opts?): Round2Result;
  round3(share, commitments, state1, state2): Uint8Array;
  combine(publicKey, msg, commitments, responses, opts?): Uint8Array | null;

  // DKG methods
  dkgSetup(sessionId): { bitmasks, holdersOf };
  dkgPhase1(partyId, sessionId): { broadcast, state };
  dkgPhase2(partyId, sessionId, state, allPhase1): { broadcast, privateToHolders };
  dkgPhase2Finalize(partyId, sessionId, ...): { shares, generatorAssignment, privateToAll };
  dkgPhase4(partyId, sessionId, ...): { broadcast };
  dkgFinalize(partyId, sessionId, ...): DKGResult;
}''')

sub_heading('19.3 State Management')

body(
    '<b>Round1State:</b> Contains #stws (Float64Array[] \u2014 hyperball samples, SENSITIVE) and '
    '#commitment (packed w vectors). Uses ES2022 #private fields. Provides destroy() for zeroization.'
)
spacer(4)
body(
    '<b>Round2State:</b> Contains #hashes (stored commitment hashes), #mu (message digest, SENSITIVE), '
    '#act (active signer bitmask), #activePartyIds. Also #private with destroy().'
)

sub_heading('19.4 FVec Layout')

body(
    'A Float64Array of size N\u00b7(K+L) representing a vector in R_q^{K+L}. First N\u00b7L floats: '
    'the z/y components. Last N\u00b7K floats: the e (error) components. Total: 256\u00b78 = 2048 '
    'floats for ML-DSA-44. The L-components are scaled by \u03bd=3.0 during hyperball sampling.'
)


# ======================================================================
# 20. API REFERENCE
# ======================================================================
section_heading('20. API Reference')

sub_heading('20.1 ThresholdMLDSA.create(securityLevel, T, N)')

table(
    ['Parameter', 'Type', 'Description'],
    [
        ['securityLevel', 'number', '44, 65, 87 (or 128, 192, 256)'],
        ['T', 'number', 'Threshold (minimum signers), 2 \u2264 T'],
        ['N', 'number', 'Total parties, T \u2264 N \u2264 6'],
    ],
    [0.22, 0.18, 0.60],
)

sub_heading('20.2 keygen(seed?)')

body(
    'Single-device key generation (for testing and development). Returns { publicKey, shares }. '
    'Optional 32-byte deterministic seed. For production use, the dealerless DKG methods (Section 9) '
    'are the correct path.'
)

sub_heading('20.3 round1(share, opts?)')

body(
    'Distributed Round 1. Returns { commitmentHash (32 bytes), state (Round1State) }. '
    'Broadcast commitmentHash to all parties. Keep state private.'
)

sub_heading('20.4 round2(share, activePartyIds, msg, hashes, state, opts?)')

body(
    'Distributed Round 2. Returns { commitment (packed bytes), state (Round2State) }. '
    'Broadcast commitment to all parties.'
)

sub_heading('20.5 round3(share, commitments, state1, state2)')

body(
    'Distributed Round 3. Returns packed partial response (Uint8Array). Throws if any commitment '
    'doesn\'t match its hash. Broadcast response to all parties.'
)

sub_heading('20.6 combine(publicKey, msg, commitments, responses, opts?)')

body(
    'Combine step. Returns standard FIPS 204 signature (Uint8Array) or null if all K_iter iterations '
    'failed. Does NOT require secret key material.'
)

sub_heading('20.7 DKG Methods')

table(
    ['Method', 'Input', 'Output'],
    [
        ['dkgSetup', 'sessionId', 'bitmasks, holdersOf'],
        ['dkgPhase1', 'partyId, sessionId', 'broadcast, state'],
        ['dkgPhase2', 'partyId, sid, state, allPhase1', 'broadcast, privateToHolders'],
        ['dkgPhase2Finalize', 'partyId, sid, state, phase1, phase2, reveals', 'shares, generators, masks'],
        ['dkgPhase4', 'partyId, sid, phase2, masks, ownMasks, shares', 'broadcast (R_j)'],
        ['dkgFinalize', 'partyId, sid, phase2, phase4, shares', 'DKGResult {publicKey, share}'],
    ],
    [0.22, 0.38, 0.40],
)

sub_heading('20.8 Byte Lengths')

table(
    ['Property', 'ML-DSA-44', 'ML-DSA-65', 'ML-DSA-87'],
    [
        ['Public key', '1,312', '1,952', '2,592'],
        ['Signature', '2,420', '3,309', '4,627'],
        ['Commitment hash', '32', '32', '32'],
        ['Polynomial (packed)', '736', '736', '736'],
        ['Commitment (2-of-2)', '5,888', '7,360', '10,304'],
        ['Response (2-of-2)', '5,888', '7,360', '10,304'],
    ],
    [0.30, 0.23, 0.23, 0.24],
)


# ======================================================================
# 21. KNOWN LIMITATIONS
# ======================================================================
section_heading('21. Known Limitations')

sub_heading('21.1 No Side-Channel Protection in JavaScript')

body(
    'JavaScript cannot guarantee constant-time operations. Branch misprediction from if/else on '
    'secret-dependent values, cache-timing attacks on array indexing, JIT compiler optimizations, '
    'and garbage collector pauses may introduce timing variations. The H1 fix addresses one specific '
    'leak, but comprehensive side-channel protection requires hardware-level guarantees.'
)

sub_heading('21.2 Float64 Platform Dependence')

body(
    'Transcendental functions are not required to be correctly rounded by IEEE 754. Cross-platform '
    'deterministic signing is NOT guaranteed. Each platform independently produces valid signatures.'
)

sub_heading('21.3 N \u2264 6 Cap')

body(
    'N is limited to 6 due to: combinatorial explosion of subsets, rapid K_iter growth, parameter '
    'table size requirements, and share storage overhead. The signature size never changes \u2014 '
    'only off-chain communication grows.'
)

sub_heading('21.4 Identifiable Aborts (Implicit Only)')

body(
    'The implementation supports identifiable abort detection implicitly (commitment hash verification '
    'catches cheating parties), but does not expose a standalone identifyAbort() method.'
)

sub_heading('21.5 DKG Limitations')

body(
    '<b>No full malicious robustness when N &lt; 2T-1:</b> If T-1 colluders all land in the same '
    'bitmask, they can bias that share. Proven non-exploitable (Theorem 6) but not provably random.'
)
spacer(4)
body(
    '<b>No robustness against corrupt mask distribution:</b> A malicious generator can send wrong '
    'mask pieces. Detected only by test signing (wrong public key \u2192 restart).'
)
spacer(4)
body(
    '<b>No proactive security / share refresh.</b> Shares are static.'
)
spacer(4)
body(
    '<b>No abort tolerance during DKG.</b> Liveness requires all N parties.'
)

sub_heading('21.6 Unaudited Implementation')

warning_box(
    'This is a port of an academic reference implementation. It has NOT undergone formal security '
    'audit. The Go reference implementation\'s audit findings have been applied, but the TypeScript '
    'port itself is unaudited. Do not use for production custody without formal review.',
    title='UNAUDITED'
)


# ======================================================================
# APPENDIX A: NOTATION REFERENCE
# ======================================================================
section_heading('Appendix A: Notation Reference')

table(
    ['Symbol', 'Meaning'],
    [
        ['R_q', '\u2124_q[X]/(X\u00b2\u2075\u2076 + 1), the polynomial ring'],
        ['q', '8,380,417 (the Dilithium prime)'],
        ['N', '256 (polynomial degree)'],
        ['K, L', 'Matrix dimensions of A \u2208 R_q^{K\u00d7L}'],
        ['T', 'Threshold (minimum signers)'],
        ['\u03b7 (eta)', 'Bound on secret key coefficients'],
        ['\u03c4 (tau)', 'Hamming weight of challenge polynomial'],
        ['\u03b3\u2081 (gamma1)', 'Masking range for z'],
        ['\u03b3\u2082 (gamma2)', 'Decomposition parameter'],
        ['\u03b2 (beta)', '\u03c4\u00b7\u03b7, norm bound adjustment'],
        ['\u03c9 (omega)', 'Maximum hint weight'],
        ['d', '13, Power2Round parameter'],
        ['\u03bd (nu)', '3.0, hyperball scaling factor'],
    ],
    [0.20, 0.80],
)

spacer(12)

table(
    ['Symbol', 'Meaning'],
    [
        ['r', 'Primary L2 radius bound'],
        ['r\'', 'Sampling hypersphere radius'],
        ['K_iter', 'Parallel signing iterations per round'],
        ['\u03c1 (rho)', 'Public randomness seed (32 bytes)'],
        ['tr', 'Public key hash (64 bytes)'],
        ['\u03bc (mu)', 'Message digest (64 bytes)'],
        ['c\u0303', 'Challenge hash (32/48/64 bytes)'],
        ['A', 'Public matrix in R_q^{K\u00d7L} (NTT domain)'],
        ['s\u2081, s\u2082', 'Secret key vectors'],
        ['t\u2081', 'Public key polynomial vector'],
        ['w', 'Commitment vector'],
        ['z', 'Response vector'],
        ['h', 'Hint vector'],
        ['\u03c3', 'Signature = (c\u0303, z, h)'],
    ],
    [0.20, 0.80],
)


# ======================================================================
# APPENDIX B: TEST COVERAGE
# ======================================================================
section_heading('Appendix B: Test Coverage')

body(
    'The PERMAFROST implementation includes <b>135 tests</b> across 7 test files covering all aspects of the protocol:'
)

sub_heading('Threshold Tests (59 tests)')

table(
    ['Category', 'Count', 'Coverage'],
    [
        ['Parameter Validation', '10', 'T<2, T>N, N>6, N<2, invalid level, all valid combos'],
        ['Key Generation', '9', 'Deterministic, random, wrong seed, share count, pk lengths'],
        ['Signing (ML-DSA-44)', '11', '2-of-3 all subsets, 2-of-2, 3-of-4, 3-of-3, 4-of-4'],
        ['Signing (ML-DSA-65/87)', '4', '2-of-3 and 2-of-2 per level'],
        ['Context & Edge Cases', '5', 'Context, wrong context, empty/large message'],
        ['Error Cases', '5', 'Insufficient shares, wrong pk, duplicate IDs'],
        ['NIST Level Mapping', '3', '128\u219244, 192\u219265, 256\u219287'],
        ['Distributed Protocol', '14', 'Full round trip, tampered commitment, state destruction'],
    ],
    [0.28, 0.12, 0.60],
)

sub_heading('Dealerless DKG Tests (55 tests)')

table(
    ['Category', 'Count', 'Coverage'],
    [
        ['Correctness', '6', 'Full 4-phase DKG for all (T,N) pairs, valid ML-DSA key verification'],
        ['Signing Compatibility', '6', 'DKG shares produce valid sigs via sign() and round1-round3'],
        ['Seed Consistency', '5', 'All holders of bitmask b derive identical seed_b'],
        ['Mask Cancellation', '5', 'sum_j R_j == sum_b w^b computed independently'],
        ['Structural Secrecy', '5', 'Each party missing at least one bitmask'],
        ['Commitment Binding', '5', 'Wrong r_{i,b} reveal detected by fellow holders'],
        ['Session Isolation', '5', 'Cross-session commitments rejected'],
        ['Generator Balance', '5', 'No party assigned excess bitmasks'],
        ['Non-holder Exclusion', '5', 'Non-holders cannot compute seed_b'],
        ['Post-DKG Test Sign', '5', 'Successful DKG always yields signable shares'],
        ['Deterministic Vectors', '3', 'Fixed-seed reproducibility across runs'],
    ],
    [0.28, 0.12, 0.60],
)

sub_heading('Standard ML-DSA Tests (21 tests)')

body(
    'All existing ML-DSA tests pass without regression after the primitives extraction refactor: '
    '8 ACVP NIST vectors, 5 basic operations, 4 hybrid tests, 3 DKG vectors, 1 error handling.'
)

sub_heading('DKG Verification Points')

table(
    ['#', 'Test', 'Description'],
    [
        ['1', 'Correctness', 'Full 4-phase DKG for all (T,N), verify valid ML-DSA key'],
        ['2', 'Signing compat', 'DKG shares produce valid signatures via sign() and round1-round3'],
        ['3', 'Seed consistency', 'All holders of bitmask b derive identical seed_b'],
        ['4', 'Mask cancellation', '\u2211_j R_j == \u2211_b w^b (both computed independently)'],
        ['5', 'Structural secrecy', 'Each party missing at least one bitmask'],
        ['6', 'Commitment binding', 'Reveal different r_{i,b} than committed \u2192 detected'],
        ['7', 'Session isolation', 'Session A commitments invalid in session B'],
        ['8', 'Generator balance', 'No party assigned > ceil(|B|/k) bitmasks'],
        ['9', 'Non-holder exclusion', 'Non-holders cannot compute seed_b from public transcript'],
        ['10', 'Post-DKG test sign', 'Successful DKG always produces signable shares'],
    ],
    [0.05, 0.20, 0.75],
)


# ======================================================================
# BUILD
# ======================================================================
_flush_heading()  # flush any trailing unbonded heading
g.build_document(doc, story)
