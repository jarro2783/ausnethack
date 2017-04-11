'use strict';

function Datatable(table, options) {
  this.page = 0
  this.table = table
  this.source = options.source
  this.total = options.total || 0
  this.elements = {}
  this.sortable = options.sortable || []
  this.sort_column = options.sort_column || 0
  this.ascending = false
  this.sort_arrows = {}
}

Datatable.prototype.next_page = function() {
  if ((this.page+1) * 10 < this.total) {
    ++this.page;
    this.request();
  }
}

Datatable.prototype.previous_page = function() {
  if (this.page > 0) {
    --this.page;
  }
  this.request();
}

Datatable.prototype.request = function() {
  datatable_request.call(this);
};

Datatable.prototype.refreshCounters = function() {
  var total = this.total
  this.elements.total.innerHTML = total
  this.elements.min.innerHTML = this.page * 10 + 1
  this.elements.max.innerHTML = Math.min((this.page+1) * 10, this.total)

  if (this.page == 0) {
    this.prevButton.disabled = true
  } else {
    this.prevButton.disabled = false
  }

  if ((this.page+1) * 10 > this.total) {
    this.nextButton.disabled = true
  } else {
    this.nextButton.disabled = false
  }
}

function datatable_request() {
  var get = [
    'page=' + this.page,
    'sort_column=' + this.sort_column
  ]

  if (this.ascending) {
    get.push('asc')
  }

  var get_string = get.join('&')

  ajax('GET', this.source + '?' + get_string,
    (result) => {
      var data = JSON.parse(result);
      var table = this.table;

      while (table.rows.length != 1) {
        table.deleteRow(1);
      }

      var rows = data.rows;

      for (var i = 0; i != rows.length; ++i) {
        var row_data = rows[i];
        var row = table.insertRow(-1);
        row.innerHTML = row_data
      }

      this.total = data.count

      this.refreshCounters()
    },
    (result) => {
    });
}

Datatable.prototype.order_by = function(index) {
  this.sort_column = index
  this.ascending = !this.ascending

  for (var i in this.sort_arrows) {
    if (i == index) {
      var name = "sortable "
      if (this.ascending) {
        name += "sort-up"
      } else {
        name += "sort-down"
      }
      this.sort_arrows[i].className = name
    } else {
      this.sort_arrows[i].className = "sortable"
    }
  }

  this.request()
}

Datatable.prototype.make_sortable = function (column, index) {
  //the column is actually the TH object at the top of the column
  //so append to its innerHTML

  var inner = document.createElement('A')
  inner.href = '#'
  inner.innerHTML = column.innerHTML
  column.replaceChild(inner, column.childNodes[0])

  column.className = "sortable"

  this.sort_arrows[index] = column

  column.onclick = () => {
    this.order_by(index)
  }
}

function datatable(table, options) {
  var dt = new Datatable(table, options);

  var next = document.createElement('button');
  next.className = "datatable"
  next.appendChild(document.createTextNode('Next'));
  next.datatable = dt;

  var previous = document.createElement('button');
  previous.className = "datatable"
  previous.appendChild(document.createTextNode('Previous'));
  previous.datatable = dt;

  var total = document.createElement('span');

  var min = document.createElement('span');
  var max = document.createElement('span');

  var p = table.parentNode;

  var div = document.createElement('div');
  div.className = 'datatable-head'
  p.insertBefore(div, p.firstChild);

  var range = document.createElement('span')
  range.className = 'datatable-range'

  range.appendChild(min);
  range.appendChild(document.createTextNode('..'));
  range.appendChild(max);
  range.appendChild(document.createTextNode(' of '));
  range.appendChild(total);

  div.appendChild(range)

  div.appendChild(previous, p.firstChild);
  div.appendChild(next, p.firstChild);

  next.onclick = () => dt.next_page();
  previous.onclick = () => dt.previous_page();

  dt.nextButton = next
  dt.prevButton = previous

  //look for th
  var header;
  var body;
  var children = table.children
  if (children[0].nodeName != 'THEAD' || children[1].nodeName != 'TBODY') {
    throw "Need a thead and tbody for datatable";
  } else {
    header = children[0];
    body = children[1];
  }

  //get the columns
  var columns = header.children[0].children
  for (var sortable in dt.sortable) {
    if (sortable > columns.length) {
      break;
    }

    var index = dt.sortable[sortable]

    dt.make_sortable(columns[index], index)
  }

  dt.sort_arrows[dt.sort_column].className = "sortable sort-down"

  var elements = dt.elements
  elements.total = total;
  elements.min = min;
  elements.max = max;

  dt.refreshCounters()
}

exports.datatable = datatable
