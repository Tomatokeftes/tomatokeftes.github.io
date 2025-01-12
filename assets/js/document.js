$(document).ready(function () {
    if (top.location.pathname === '/publications/') {
        fetch("https://pub.orcid.org/v3.0/0009-0003-5579-5488/works", {
            headers: { "Accept": "application/xml" }
        })
        .then(response => response.text())
        .then(xmlString => {
            // Parse the XML
            let parser = new DOMParser();
            let xml = parser.parseFromString(xmlString, "application/xml");

            // Extract publication groups
            let groups = xml.getElementsByTagName("activities:group");
            let html_str = '<ul>';

            for (let i = 0; i < groups.length; i++) {
                let summaries = groups[i].getElementsByTagName("work:work-summary");

                for (let j = 0; j < summaries.length; j++) {
                    let summary = summaries[j];

                    // Extract title
                    let title = summary.getElementsByTagName("common:title")[0].textContent;

                    // Extract DOI URL
                    let doi = summary.querySelector("common\\:external-id-url, external-id-url");
                    let doi_url = doi ? doi.textContent : "#";

                    // Extract publication date
                    let year = summary.querySelector("common\\:publication-date common\\:year").textContent;
                    let month = summary.querySelector("common\\:publication-date common\\:month")?.textContent || "";
                    let day = summary.querySelector("common\\:publication-date common\\:day")?.textContent || "";
                    let date = `${year}-${month}-${day}`.replace(/-$/, "").replace(/-$/, ""); // Format date

                    // Extract journal title
                    let journal = summary.getElementsByTagName("work:journal-title")[0]?.textContent || "Unknown Journal";

                    // Build HTML
                    html_str += `
                        <li>
                            <strong><a href="${doi_url}" target="_blank">${title}</a></strong>
                            <br>${journal} (${date})
                        </li>
                    `;
                }
            }

            html_str += '</ul>';
            $('#publications').html(html_str);
        })
        .catch(error => {
            console.error("Error fetching ORCID data:", error);
            $('#publications').html('<p>Unable to load publications at this time.</p>');
        });
    }
});
