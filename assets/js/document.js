$(document).ready(function () {
    if (top.location.pathname === '/research/') {
        var x = new XMLHttpRequest();
        // Change the link to the appropriate one.
        x.open("GET", "https://dblp.org/pid/167/1074.xml", true);
        x.onreadystatechange = function () {
            if (x.readyState == 4 && x.status == 200) {
                var publications = x.responseXML;
                var r = publications.getElementsByTagName("r");
                var html_str = '<ul>';

                for (var i = 0; i < r.length; i++) {
                    html_str += "<li>"
                    console.log(r[i].innerHTML);

                    var authors = r[i].getElementsByTagName('author');
                    var authors_str = ''
                    for (var j = 0; j < authors.length; j++) {
                        authors_str += authors[j].innerHTML
                        if (j < authors.length - 1) {
                            authors_str += ', '
                        } else {
                            authors_str += ';'
                        }
                    }
                    html_str += authors_str

                    var title_str = " " + r[i].getElementsByTagName('title')[0].innerHTML;
                    var doi = r[i].getElementsByTagName('ee')[0].innerHTML;

                    html_str += "<strong> <i> <a href='" + doi + "' target='_blank'>" + title_str + "</a> </i> </strong>;"

                    var journal = r[i].getElementsByTagName('journal')[0];
                    if (!journal) {
                        var journal = r[i].getElementsByTagName('booktitle')[0];
                    }
                    html_str += " " + journal.innerHTML + " ";

                    var year = r[i].getElementsByTagName('year')[0];
                    html_str += year.innerHTML + '.';

                    html_str += "</li>";
                }
                html_str += "</ul>";
            }
            $('#publications').html(html_str);
        };
        x.send(null);
    }


});