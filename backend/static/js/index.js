$(document).ready(function() {
    $("#menu-toggle").click(function(e) {
        e.preventDefault();
      $("#wrapper").toggleClass("toggled");
    });

    $('#btn-refresh').click(function(){
        $.ajax({
            url: '/refresh',
            type: 'get',
            dataType: 'json',
            success: function(res) {
                console.log(res['names'].length);
                for (let i = 0; i < res['names'].length; i++) {
                    if (i % 2 == 0) {
                        $('#row-left').append('<table class="table"><tr><th>Firstname</th><th>Lastname</th></tr>'
                                                                   + '<tr><td>' + res.names[i]['firstname'] + '</td><td>' + res.names[i]['lastname'] + '</td></tr>'
                                              + '</table>');
                       
                    } else {
                        $('#row-right').append('<table class="table"><tr><th>Firstname</th><th>Lastname</th></tr>'
                                                                   + '<tr><td>' + res.names[i]['firstname'] + '</td><td>' + res.names[i]['lastname'] + '</td></tr>'
                                              + '</table>');
                    }
                }
            }
        });
    });
});
