function scrollFunction(){
    document.body.scrollTop>20||document.documentElement.scrollTop>20?mybutton.style.display="block":mybutton.style.display="none"
}
function topFunction(){
    document.body.scrollTop=0,document.documentElement.scrollTop=0
}
mybutton=document.getElementById("myBtn");
window.onscroll=function(){scrollFunction()};

$(document).ready(function() {
    let table = $('#all-subs').dataTable({
        dom: "<'#searchBox'>frtip",
        "order": [[ 3, 'des' ]],
        "columnDefs": [ {
            "searchable": false,
            "orderable": false,
            "targets": 0
        } ],
    });

    $(".dataTables_info").appendTo("#customInfo");

    table.api().on('order.dt', function () {
        table.api().column(0, {order:'applied'}).nodes().each(function (cell, i) {
            cell.innerHTML = i+1;
        });
    }).draw();

    $('#searchBox').keyup(function(){
        $('#all-subs').DataTable().search($(this).val()).draw() ;
    });
});
