
//--------------prep.html JAVASCRIPT----------------
//Opens the Chemistry Reference Document in a new tab
function open_pdf(path){
    window.open(path,'Reference Table');
};

//Selects or deselects all the unit buttons
//Commented lines support a different version of buttons
function checkAllUnits(){
    var allSelect = true;
    var x = document.getElementsByName("units");
    for (var i = 0; i < x.length; i++) {
        if (x[i].checked == false)
            allSelect = false;
        x[i].checked = true;
        //x[i].classList.add("active");
        //x[i].setAttribute("aria-pressed", "true");
    }
    if(allSelect)
        for (i = 0; i < x.length; i++){
            x[i].checked = false;
            //x[i].classList.remove("active");
            //x[i].setAttribute("aria-pressed", "false");
        }
};

//Selects or deselects all the year buttons
function checkAllTests(){
    var allSelect = true;
    var x = document.getElementsByName("exams");
    for (var i = 0; i < x.length; i++) {
        if (x[i].checked == false)
            allSelect = false;
        x[i].checked = true;
    }
    if(allSelect)
        for (i = 0; i < x.length; i++)
            x[i].checked = false;

};

//--------------Question.html JAVASCRIPT----------------
//checks the button and highlights it, and sets it to the answer
function check_button(letter) {
    var letters = ["a","b","c","d"];
    for(var i in letters)
        if(document.getElementById(letters[i]).disabled == false )
            document.getElementById(letters[i]).className = "btn";
    document.getElementById(letter).className = "btn btn-primary";
    document.getElementById('answer').value = letter;
};

//When the page is loaded, disables and colors the buttons previous clicked
function setButtons(correct, pre_ans, index, total){
    if(pre_ans.length < 1)
        return;
    last_answer = pre_ans.slice(pre_ans.length-1, pre_ans.length);
    //Set all the buttons to the correct values and update the progress bar
    if(correct == "True"){
        document.getElementById(last_answer).className = "btn btn-success";
        document.getElementById(last_answer + "_text").color = "green";
        var letters = ["a","b","c","d"];
        for(var i in letters)
            document.getElementById(letters[i]).disabled = true;
        document.getElementById("skip").disabled = true;
        document.getElementById("submit").textContent = "Continue";
        document.getElementById("answer").value = "continue";
        document.getElementById("submit").className = "btn btn-success btn-block";
        update_progress(index, total)
    }else if (correct == "False"){
        //disable the last answer
        document.getElementById(last_answer).className = "btn btn-danger";
        document.getElementById(last_answer).disabled  = true;
        document.getElementById(last_answer + "_text").color = "red";
        document.getElementById(last_answer + "_text").style.setProperty("text-decoration", "line-through");
    }
    //disable all previous answers
    for(var i = 0; i < pre_ans.length - 1; i++){
        document.getElementById(pre_ans[i] + "_text").color = "red";
        document.getElementById(pre_ans[i]).disabled  = true;
        document.getElementById(pre_ans[i]).className = "btn btn-danger";
        document.getElementById(pre_ans[i] + "_text").style.setProperty("text-decoration", "line-through");
    }
};

//Updates the progress bar
function update_progress(index, total){
    var percent = ((index) / total) * 100;
    percent = Math.round(percent);
    document.getElementById("progress_bar").style.width = percent + "%";
    document.getElementById("progress_bar").textContent = percent + "%";
};


//--------------Result.html JAVASCRIPT----------------
//Puts data into the pie chart breaking down the questions wrong by unit
function pieChartFunc(miss_by_unit){
     var list_MBY = miss_by_unit.substring(1, miss_by_unit.length - 1).split(",");
     google.charts.load('current', {'packages':['corechart']});
     google.charts.setOnLoadCallback(drawChart);

     function drawChart() {
        var data = google.visualization.arrayToDataTable([
          ['Unit',       'Questions Missed'],
          ['Unit One',   parseInt(list_MBY[0])],
          ['Unit Two',   parseInt(list_MBY[1])],
          ['Unit Three', parseInt(list_MBY[2])],
          ['Unit Four',  parseInt(list_MBY[3])],
          ['Unit Five',  parseInt(list_MBY[4])],
          ['Unit Six',   parseInt(list_MBY[5])],
          ['Unit Seven', parseInt(list_MBY[6])],
          ['Unit Eight', parseInt(list_MBY[7])],
          ['Unit Nine',  parseInt(list_MBY[8])],
          ['Unit Ten',   parseInt(list_MBY[9])],
          ['Unit Eleven',parseInt(list_MBY[10])],
          ['Unit Twelve',parseInt(list_MBY[11])]
        ]);
        var options = {
          title: 'Questions Missed By Unit',
          chartArea: {left:20,top:0,width:'100%',height:'100%'}
        };
        var chart = new google.visualization.PieChart(document.getElementById('piechart'));
        chart.draw(data, options);
     }
};

//animates the circe counting to the percent questions correct
function animatePercentChart(stopVal){
    var elm = document.getElementById("percentchart");
    var me = setInterval(anim, 25);

    function anim(){
        name = elm.className.substring(0, elm.className.lastIndexOf("p") + 1);
        number = parseInt(elm.className.substring(elm.className.lastIndexOf("p") + 1, elm.className.length));
        number += 1;
        if(number > stopVal)
            clearInterval(me);
        else{
            elm.className = name + number;
            document.getElementById("percentChartText").textContent = number + "%";
        }
    }
};

//Puts data into the pie chart breaking down the questions wrong by attempt number
function piechartAnsFunc(trys, skips){
     var list_trys = trys.substring(1, trys.length - 1).split(",");
     google.charts.load('current', {'packages':['corechart']});
     google.charts.setOnLoadCallback(drawChart);
     function drawChart() {
        var data = google.visualization.arrayToDataTable([
          ['Try',                   'The x attempt'],
          ['First Try (Correct)',   parseInt(list_trys[0])],
          ['Second Try',            parseInt(list_trys[1])],
          ['Third Try',             parseInt(list_trys[2])],
          ['Last Try',              parseInt(list_trys[3])],
          ['Skipped',               parseInt(skips)]
        ]);
        var options = {
          title: 'Answer Attempts',
          chartArea: {left:20,top:0,width:'100%',height:'100%'}
        };
        var chart = new google.visualization.PieChart(document.getElementById('piechartAns'));
        chart.draw(data, options);
     }
};

//Puts data into the pie chart breaking down the questions skipped by unit
function piechartSkipFunc(skipped){
     var list_skipped = skipped.substring(1, skipped.length - 1).split(",");
     google.charts.load('current', {'packages':['corechart']});
     google.charts.setOnLoadCallback(drawChart);
     function drawChart() {
        var data = google.visualization.arrayToDataTable([
          ['Unit',       'Questions Missed'],
          ['Unit One',   parseInt(list_skipped[0])],
          ['Unit Two',   parseInt(list_skipped[1])],
          ['Unit Three', parseInt(list_skipped[2])],
          ['Unit Four',  parseInt(list_skipped[3])],
          ['Unit Five',  parseInt(list_skipped[4])],
          ['Unit Six',   parseInt(list_skipped[5])],
          ['Unit Seven', parseInt(list_skipped[6])],
          ['Unit Eight', parseInt(list_skipped[7])],
          ['Unit Nine',  parseInt(list_skipped[8])],
          ['Unit Ten',   parseInt(list_skipped[9])],
          ['Unit Eleven',parseInt(list_skipped[10])],
          ['Unit Twelve',parseInt(list_skipped[11])]
        ]);
        var options = {
          title: 'Questions Skips',
          chartArea: {left:20,top:0,width:'100%',height:'100%'}
        };
        var chart = new google.visualization.PieChart(document.getElementById('piechartSkip'));
        chart.draw(data, options);
     }
};

//Not used in the current user interface
//Expand and collapse button options
function expand(elm){
    if(document.getElementById(elm).style.display == "none")
		document.getElementById(elm).style.display = "block";
	else
		document.getElementById(elm).style.display = "none";
};