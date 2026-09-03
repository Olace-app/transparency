# Security Policy

## Reporting

Email **security@olace.app** with what you found, how to reproduce it, and what you believe the impact is. PGP is not required; if you would like an encrypted channel, say so in an initial message and we will arrange one.

You will receive an acknowledgment within 3 business days and a substantive assessment within 14 days.

## Coordinated disclosure

We ask for up to **90 days** from your report to ship a fix before public disclosure. If we fix it sooner, disclose sooner; if something structural needs longer, we will explain why and agree on a date with you. Credit is yours unless you prefer anonymity.

## Scope

- The Olace app (desktop, mobile, web) and desktop daemon
- The Olace backend and its API surface
- The public crypto repos: [olace-crypto-dart](https://github.com/Olace-app/olace-crypto-dart), [olace-e2ee-go](https://github.com/Olace-app/olace-e2ee-go)
- The claims in this repo's white paper: a demonstration that a claim is false is a valid report

Out of scope: denial of service through volume, findings that require a compromised device or OS, social engineering of Olace staff, and third-party services (OpenRouter, payment processors) except where Olace's integration is the flaw.

## Safe harbor

Good-faith research against **your own accounts and your own devices** is welcome. We will not initiate or support legal action against you for it, and we consider such research authorized under applicable anti-hacking and anti-circumvention laws. If a third party pursues you over research conducted within this policy, we will state on record that it was authorized. Do not access other people's data, degrade the service for others, or retain data you encounter unintentionally; if that happens despite your precautions, stop, report it, and delete what you hold.

## Bounty

Olace does not currently operate a paid bounty program. Reports are credited, and this policy will be revisited as the product grows.
