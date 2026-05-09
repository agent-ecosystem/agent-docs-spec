{{ with .Title }}# {{ . }}{{ end }}

{{ partial "llms-directive.md" . }}
{{ .RawContent }}
