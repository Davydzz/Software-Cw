function createTable(tableData) {
    var table = document.getElementById('thisTable');
    var tablediv = document.getElementById('tablediv');
    var form = document.getElementById('eventform');
    var tableBody = document.createElement('tbody');
    tableData.forEach(function (rowData, index) {
        console.log(index);
        var row = document.createElement('tr');
        for (var i = 0; i < 4; i++) {
            var cellData = rowData[i];
            if (i == 3) {
                var role = rowData[i - 1]

                switch (role) {
                    case "host":
                        var cell = document.createElement('td');
                        var button = document.createElement('button');
                        button.name = "joinButton";
                        button.value = index;
                        cell.appendChild(button);
                        break;
                    case "attendee":
                        var cell = document.createElement('td');
                        var button = document.createElement('button');
                        button.name = "joinButton";
                        button.value = index;
                        cell.appendChild(button);
                }


            } else {
                var cell = document.createElement('td');
                cell.appendChild(document.createTextNode(cellData));
            }
            row.appendChild(cell);
        }
        tableBody.appendChild(row);
    });

    table.appendChild(tableBody);
    form.insertBefore(table, form.firstChild);
    tablediv.appendChild(form);
}