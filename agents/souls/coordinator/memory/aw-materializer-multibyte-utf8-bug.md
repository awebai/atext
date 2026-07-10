---
name: aw-materializer-multibyte-utf8-bug
description: aw materializer rejects YAML folded block scalars (mission: >) in profile.yaml — use >- or plain scalars until aw .3.24.
metadata:
  type: project
---

aw's profile materialize fails with `profiles/<id>/profile.yaml:<field>: control
characters are not allowed` when a required string field uses a YAML FOLDED block
scalar (`mission: >`). Go yaml decodes `>` with a trailing newline, and aw's
`profilepack.validateRequiredString` rejects the LF via `unicode.IsControl`.

It is NOT a multibyte-UTF-8 bug (my first, WRONG hypothesis): em-dash, accented,
or curly-quote text in a PLAIN one-line scalar materializes fine. The trigger is
purely the folded-scalar trailing newline. The v0.2.0 reviewer profile had both
em-dashes AND `mission: >`; the ASCII-only v0.2.1 STILL failed because it kept the
bare `>`. v0.2.2 is the real fix: folded-strip `>-`, which strips the trailing
newline.

Rule until aw `default-aaas.3.24` lands (aw owns the durable fix — free-text
validation should permit LF/TAB, or trim block-scalar trailing whitespace): in
profile.yaml / pack.yaml required-string fields use `>-` (folded-strip) or a plain
scalar — never a bare `>` or `|`. The engineering pack is v0.2.2 for this. See
[[engineering-pack-home]].

Diagnostic lesson: a byte-scan falsely implicated the em-dash (its UTF-8
continuation bytes 0x80/0x94 look like C1 controls if scanned byte-wise). The real
proof came from aw-developer reproducing with the exact bytes and finding ASCII-
only STILL failed. Don't stop at the first plausible cause — confirm by reproduction.
