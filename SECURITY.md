# Security Policy

## Reporting

Email **security@olace.app** with what you found, how to reproduce it, and what you believe the impact is. PGP is not required; if you want an encrypted channel, say so in a first plain message and we will arrange one.

You will get an acknowledgment within 72 hours and a substantive assessment within 14 days.

## Coordinated disclosure

We ask for up to **90 days** from your report to ship a fix before public disclosure. If we fix it sooner, disclose sooner; if we need longer for something structural, we will explain why and agree on a date with you. Credit is yours unless you prefer anonymity.

## Scope

- The Olace app (desktop, mobile, web) and desktop daemon
- The Olace backend and its API surface
- The public crypto repos: [olace-crypto-dart](https://github.com/Olace-app/olace-crypto-dart), [olace-e2ee-go](https://github.com/Olace-app/olace-e2ee-go)
- The claims in this repo's white paper: if you can show a claim is false, that is a valid report

Out of scope: denial of service through volume, findings that require a compromised device or OS, social engineering of Olace staff, and third-party services (OpenRouter, payment processors) except where Olace's integration is the flaw.

## Safe harbor

Good-faith research against **your own accounts and your own devices** is welcome and will not be met with legal action. Do not access other people's data, degrade the service for others, or retain data you stumbled into; if you brush against someone else's data despite trying not to, stop, report it, and delete what you hold.

## No bounty yet

Olace is a small company pre-launch. There is currently no paid bounty program; we say this up front rather than imply one. Reports are credited, and that policy will be revisited as the product grows.
