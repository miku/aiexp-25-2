SHELL = /bin/bash

opus4-bib-info-2025-pdf.txt:
	jq -rc 'select(any(.type[]?; IN("Konferenzfolien", "Konferenzabstract")) and .date[0] == "2025") | .dc_identifier[]?' ../notes/opus4-bib-info.json | grep 'pdf$' > opus4-bib-info-2025-pdf.txt

