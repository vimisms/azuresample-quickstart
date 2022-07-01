function searchRecommendations() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("recommendationssearch");
    filter = input.value.toUpperCase();
    table = document.getElementById("recomtable");
    tr = table.getElementsByTagName("tr");
    searchCol = filter.split(":")[0];
    searchtxt = filter.split(":")[1];

    for (i = 0; i < tr.length; i++) {
        if (searchCol === "IMPACT") {
            td = tr[i].getElementsByTagName("td")[1];
            if (td) {
                txtValue = td.textContent || td.innerText;
                if (txtValue.toUpperCase().indexOf(filter.split(":")[1]) > -1) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }

        } else if (searchCol === "CATEGORY") {
            td = tr[i].getElementsByTagName("td")[0];
            console.log("You selected category filter")
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