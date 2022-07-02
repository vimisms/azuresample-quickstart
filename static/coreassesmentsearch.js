function searchHealthy() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("defheasearch");
    filter = input.value.toUpperCase();
    table = document.getElementById("defhealthy");
    tr = table.getElementsByTagName("tr");

    searchCol = filter.split(":")[0];
    searchtxt = filter.split(":")[1];

    for (i = 0; i < tr.length; i++) {
        if (searchCol === "RESOURCE") {
            td = tr[i].getElementsByTagName("td")[0];
            if (td) {
                txtValue = td.textContent || td.innerText;
                if (txtValue.toUpperCase().indexOf(filter.split(":")[1]) > -1) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }
        } else if (searchCol === "RULE") {
            td = tr[i].getElementsByTagName("td")[1];
            if (td) {
                txtValue = td.textContent || td.innerText;
                if (txtValue.toUpperCase().indexOf(filter.split(":")[1]) > -1) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }

        }
    }

}

function searchUnHealthy() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("defunheasearch");
    filter = input.value.toUpperCase();
    table = document.getElementById("defunhealthy");
    tr = table.getElementsByTagName("tr");

    searchCol = filter.split(":")[0];
    searchtxt = filter.split(":")[1];

    for (i = 0; i < tr.length; i++) {
        if (searchCol === "RESOURCE") {
            td = tr[i].getElementsByTagName("td")[0];
            if (td) {
                txtValue = td.textContent || td.innerText;
                if (txtValue.toUpperCase().indexOf(filter.split(":")[1]) > -1) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }
        } else if (searchCol === "RULE") {
            td = tr[i].getElementsByTagName("td")[1];
            if (td) {
                txtValue = td.textContent || td.innerText;
                if (txtValue.toUpperCase().indexOf(filter.split(":")[1]) > -1) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }

        }
    }

}