"""Redact push-protected account identifiers in the published trace, not its source."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
REC = ROOT / 'records'

def main():
    path = REC / '017_trace_impl-025.json'
    events = json.loads(path.read_text())
    pattern = re.compile(r'\bAC[a-fA-F0-9]{32}\b')
    manifest = []
    for event in events:
        original_path = Path(event['path'])
        original_bytes = original_path.read_bytes()
        original = json.loads(original_bytes).get('content', '')
        matches = list(pattern.finditer(original))
        if not matches:
            continue
        redacted = pattern.sub('[REDACTED_TWILIO_ACCOUNT_IDENTIFIER]', original)
        assert event['content'] in (original, redacted)
        event['content'] = redacted
        manifest.append({
            'event': event['id'], 'field': 'content', 'original_path': str(original_path),
            'original_file_sha256': hashlib.sha256(original_bytes).hexdigest(),
            'original_content_sha256': hashlib.sha256(original.encode()).hexdigest(),
            'export_content_sha256': hashlib.sha256(redacted.encode()).hexdigest(),
            'redacted_spans_in_original': [[m.start(), m.end()] for m in matches],
            'replacement': '[REDACTED_TWILIO_ACCOUNT_IDENTIFIER]',
        })
    assert len(manifest) == 1 and manifest[0]['event'] == 16
    path.write_text(json.dumps(events, ensure_ascii=False, indent=2) + '\n')
    (REC / '017_trace_redactions.json').write_text(json.dumps({
        'reason': 'GitHub push protection rejected Twilio Account String Identifier in impl-025 event16; redact published copy without bypassing protection.',
        'original_sources_unchanged': True, 'changes': manifest,
    }, ensure_ascii=False, indent=2) + '\n')
    print('Redacted 2 account-identifier occurrences in impl-025 event16; source unchanged.')

if __name__ == '__main__':
    main()
