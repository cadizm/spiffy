
$(function() {
    $.get('/api/profile/').done(
        function(data) {
            $("#profile_name").html(data.profile._source.name);
            $("#profile_bio").html(data.profile._source.bio);
            $("#profile_pic").attr("src", data.profile._source.pic);
        }
    );
});
