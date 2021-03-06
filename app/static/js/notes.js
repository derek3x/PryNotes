function save_note(id, bookid, refresh, secret) {
    var phrase;
    if (secret == 'True') {
        phrase=prompt("Please enter a secret key.  We can not retrieve this, so type carefully.  You can change your secret key now if you want to");              
    }    
    $('#loading').css({'display': 'inline'});
    $.post('/editor', {
        note: id,
        book: bookid,
        refresh: refresh,
        phrase: phrase,
        text: $('#summernote').code()
    }).done(function (save_notes) {
        $('#summernote').code(save_notes['text']);
        $('#loading').css({'display': 'none'});        
        $("#save_btn_span").removeClass('glyphicon glyphicon-floppy-disk').addClass('glyphicon glyphicon-floppy-saved');
        if (save_notes['refresh'] == 'True') {
            location.reload();
        }

    });
}

function select_note(id, bookid, booktitle, secret) {
    var phrase;
    if (secret == 'True') {
        phrase=prompt("Please enter your secret key to get your note");              
    }    
    document.getElementById("notebookchange").className = "btn btn-default dropdown-toggle btn-sm";
    document.getElementById("save_btn").className = "btn btn-primary";
    document.getElementById("save_btn").href = "javascript:save_note('" + id + "','" + bookid + "','False','" + secret + "');";
    document.getElementById("share_link").href = "/create_share/" + id;
    document.getElementById("share_link_qr").href = "/create_share_qr/" + id;
    var arrow = ' <span class="caret"></span>'
    document.getElementById("notebookchange").innerHTML = booktitle + arrow;
    jQuery.post('/select_note', {
        note_id: id,
        phrase: phrase
    }).done(function (select_note) {
        $('#summernote').code(select_note['text']);
        var localTime = moment.utc(select_note['stamps']).toDate();
        localTime = moment(localTime).format('MMMM Do YYYY, h:mm:ss a');
        $('#note_header').html(select_note['title']);
        $('#note_footer').html(localTime);
        $('#to_pdf').attr("href", '/' + select_note['title'] + '_' + id + '.pdf')
    });
}

function caret_click(noteid, notetitle) {
    document.getElementById("hidden_note_id").value = noteid;
    document.getElementById("new_title").value = notetitle;
}

function caret_merge(noteid) {
    document.getElementById("merge_note_id").value = noteid;
}

function caret_encrypt(noteid) {
    jQuery.confirm({
        text: "This will encrypt your note with your own password/passphrase.  This is a secure way to store important information as we can not decrypt this if we wanted to.  We will then encrypt your note again (twice) our normal way.  We will never know your password.  Don't forget it!",
        confirm: function() {
            var phrase;
            phrase=prompt("Please enter your secret key.  We can not retrieve this, so type very carefully.");
            if (phrase!=null){
                $.post('/secret_notes/' + noteid, {
                    phrase: phrase
                }).done(function(secret_notes) {
                    location.reload();
                });
            }             
        },
            cancel: function() {
                //Do Nothing
            }
    });
}

function caret_clickNB(bookid, booktitle) {
    document.getElementById("hidden_book_id").value = bookid;
    document.getElementById("new_nbtitle").value = booktitle;
    document.getElementById("hidden_nb_id2").value = bookid;
}

function caret_clickFC(fcid, fctitle) {
    document.getElementById("hidden_fc_id").value = fcid;
    document.getElementById("new_fctitle").value = fctitle;
}

function newnoteid(ids) {
    document.getElementById("hidden2").value = ids;
}

function new_notebook_in_fc(fc_id) {
    jQuery('#new_notebook_in_fc').modal()
    document.getElementById("hidden_fc_id2").value = fc_id;
}

function changenotebook(bookid, booktitle) {
    var arrow = ' <span class="caret"></span>'
    document.getElementById("notebookchange").innerHTML = booktitle + arrow;
    var ref = document.getElementById("save_btn").href
    var patt1 = /[0-9]+/;
    var result = ref.match(patt1);
    var ref2 = ref.slice(-8);
    var patt2 = /[a-zA-Z]+/;
    var passphrase = ref2.match(patt2);
    document.getElementById("save_btn").href = "javascript:save_note('" + result + "','" + bookid + "','True', '" + passphrase + "');";
}
jQuery(".confirm").confirm();
jQuery(".confirmnb").confirm({
    text: "Are you sure you want to delete the Notebook and all Notes in it?",
    title: "Confirmation Required"
});
jQuery(".confirmfc").confirm({
    text: "Are you sure you want to delete the File Cabinet?  The Notebooks and Notes will survive this deletion.",
    title: "Confirmation Required"
});
jQuery(".confirmaccount").confirm({
    text: "Are you sure you want to delete your account?  This will remove everything and you will never be able to get it back.",
    title: "Confirmation Required"
});
jQuery(".confirm_enc").confirm({
    text: "This will encrypt your note with your own password.  This is a very secure way to store important information.  We will never know your password.  Don't forget it!",
    title: "Confirmation Required"
});

function openWin() {
    var w = window.open();
    var html = $("#summernote").code();
    var title = $('#note_header').html();
    $(w.document.body).html(html);
    w.document.title = title;
    w.print();
    w.close();
}
function openWin_shared() {
    var w = window.open();
    var html = $(".summernote").code();
    var title = $('#note_header').html();
    $(w.document.body).html(html);
    w.document.title = title;
    w.print();
    w.close();
}
jQuery('input[id=upload]').change(function () {
    var text = $('#summernote').code();
    var filer = this.files[0];
    var form_data = new FormData();
    form_data.append('file', $('input[type=file]')[0].files[0]);
    if (filer.size > 16 * 1024 * 1024) {
        alert("That file is just simply too large.  Please add smaller files")
    } else {
        $('#loading').css({
            'display': 'inline'
        })
        $.ajax({
            type: 'POST',
            url: '/upload',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: false,
            success: function (data) {
                if (data['link'] != 'None') {
                    var link = "<br><a href=\"" + data['link'] + "\">Attached File</a>";
                    $('#summernote').code(text + link);
                    $('#save_btn').click();
                    $('#loading').css({
                        'display': 'none'
                    });
                } else {
                    alert("Not Supported: " + data['mime']);
                }
            },
        });
    }

});
