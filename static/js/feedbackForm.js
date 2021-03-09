function createTable(tableData) {
    var table = document.getElementById('thisTable');
    var tablediv = document.getElementById('tablediv');
    var form = document.getElementById('feedbackform');
    var tableBody = document.createElement('tbody');

    tableData.forEach(function (rowData) {
        var row = document.createElement('tr');
        for (var i = 0; i < 3; i++) {
            var cellData = rowData[i];
            if (i == 2) {
                switch (cellData) {
                    case "Star Rating":
                        var cell = document.createElement('td');
                        var sel = document.createElement('select');
                        sel.name = "starRating"
                        var values = [
                            "",
                            "☆",
                            "☆☆",
                            "☆☆☆",
                            "☆☆☆☆",
                            "☆☆☆☆☆"
                        ];
                        var options = values.map(value => { return `<option value="${value}">${value}</option>)` });
                        sel.innerHTML = options;
                        cell.appendChild(sel);
                        break;
                    case "Text":
                        var cell = document.createElement('td');
                        var textbox = document.createElement('input');
                        textbox.name = "text"
                        cell.appendChild(textbox);
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