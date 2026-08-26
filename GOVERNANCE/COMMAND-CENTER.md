# GIA Command Center lock

Source: GIA Command Center skill + Master SOP dashboard rules.

## One UI
- One left-side menu
- One home / overview
- GIA center stage
- Live activity + execution trail
- Factory View and Normal View only
- No extra dashboards, no template explosion

## Terminals inside the same UI
- GIA Chat
- Gemini CLI panel
- Grok Build CLI panel
- System / VPS shell (permission gated)
- Local terminal

Never launch these as full-screen apps that replace the dashboard.

## Mobile (iPhone Safari)
- Stacked or swipe panels, not tiny side-by-side
- Large buttons for status / logs / restart
- Free-text shell only after unlock
- No password fields except existing auth
- Chat first, then Terminal / Status / Agents

## Security
- Permission-first for destructive or remote commands
- Log timestamp, user, command, result
- No raw passwords in frontend
