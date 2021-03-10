function displayStars(numStars) {
    var stars = document.createElement("div");

    for (var x = 0; x < 5; x++) {
      var star = document.createElement("span");

      if (x < numStars) {
        star.className = "fa fa-star checked";
      } else {
        star.className = "fa fa-star";
      }

      stars.appendChild(star);
    }
    
    return stars;
  }

  function createTable(tableData) {
    var table = document.getElementById("thisTable");
    var tablediv = document.getElementById("tablediv");
    var tableBody = document.createElement("tbody");

    tableData.forEach(function (rowData, index) {
      var row = document.createElement("tr");
      for (var i = 0; i < 4; i++) {
        var cellData = rowData[i];
        if (i == 1) {
          switch (cellData) {
            case "Star Rating":
              var cell = document.createElement("td");
              var stars = displayStars(rowData[2]);
              cell.appendChild(stars);

              break;
            case "Text":
              var cell = document.createElement("td");
              cell.appendChild(document.createTextNode(rowData[2]));
          }
        } else if (i == 3) {
          var cell = document.createElement("td");
          cell.appendChild(document.createTextNode(cellData));
        } else if (i == 0) {
          var cell = document.createElement("td");
          cell.appendChild(document.createTextNode(cellData));
        }
        row.appendChild(cell);
      }
      tableBody.appendChild(row);
    });

    table.appendChild(tableBody);
    tablediv.appendChild(table);
  }