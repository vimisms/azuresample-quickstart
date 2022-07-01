function searchActivity() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("logsearch");
    filter = input.value.toUpperCase();
    table = document.getElementById("activitylogtable");
    tr = table.getElementsByTagName("tr");
    console.log("Able to call JS");
    searchCol = filter.split(":")[0];
    searchtxt = filter.split(":")[1];
    console.log(searchCol);
    console.log(searchtxt);
    console.log(tr.length);
    for (i = 0; i < tr.length; i++) {
        if (searchCol === "ACTIVITY") {
            td = tr[i].getElementsByTagName("td")[0];
            if (td) {
                txtValue = td.textContent || td.innerText;
                if (txtValue.toUpperCase().indexOf(filter.split(":")[1]) > -1) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }
        } else if (searchCol === "CALLER") {
            td = tr[i].getElementsByTagName("td")[1];
            console.log("You selected caller filter")
            if (td) {
                txtValue = td.textContent || td.innerText;
                if (txtValue.toUpperCase().indexOf(filter.split(":")[1]) > -1) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }

        } else if (searchCol === "CATEGORY") {
            td = tr[i].getElementsByTagName("td")[2];
            console.log("You selected category filter")
            if (td) {
                txtValue = td.textContent || td.innerText;
                if (txtValue.toUpperCase().indexOf(filter.split(":")[1]) > -1) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }

        } else if (searchCol === "STATUS") {
            td = tr[i].getElementsByTagName("td")[6];
            console.log("You selected Status filter")
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