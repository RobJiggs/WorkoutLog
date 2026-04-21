

document.addEventListener("DOMContentLoaded", () => {
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById("wsdate");

    if (dateInput) {
        dateInput.value = today;
    }
});

let createsesh = document.getElementById("create-sesh");
createsesh.addEventListener("click", async () => {


  let dropdown = document.querySelector(".session-type");
  let select=dropdown.value

  let dateput = document.getElementById("wsdate");

  let datevalue=dateput.value

  formjson2= JSON.stringify({ date:datevalue,work:select })
  let requestsesh = new Request("http://127.0.0.1:8000/worksession", {
  method: 'POST',
  body: formjson2,
  headers: new Headers({
    'Content-Type': 'application/json; charset=UTF-8'
  })
});

fetch(requestsesh)
  .then(function() {
   window.location.href = "http://127.0.0.1:8000"
  }).catch(error => console.error('Error fetching:', error));






  }
)

document.querySelectorAll("[class*=workoutbutton]").forEach((button) => {
  button.addEventListener("click", async () => {
    const logid=button.getAttribute("class")
    const logvalue=logid.match(/\d+$/)[0]
    const addid="additional"+logvalue
    let additional=document.getElementById(addid);
    nameid= "form-name"+logvalue;
    descid="form-desc"+logvalue;
    additional.innerHTML=`<form class="form-group">
    <label for="${nameid}" class="form-label">Name</label>
    <br> <input type="text" id=${nameid} value="" ><br>
    <label for="${descid}">Description</label>
    <br><input type="text" id="${descid}" value=""></form>
    <button class="savebutton${logvalue} btn btn-success">Save</button>
    `;
    button.style.display="none"
    document.querySelectorAll("[class*=savebutton]").forEach((button) => {
    button.addEventListener("click", async () => {

    let name1= document.getElementById(nameid).value
    let desc1= document.getElementById(descid).value
    let wsnum =logid.match(/\d+$/)[0]

    formjson= JSON.stringify({name:name1,desc:desc1,session_id:parseInt(wsnum)})


let request = new Request("http://127.0.0.1:8000/workouts", {
  method: 'POST',
  body: formjson,
  headers: new Headers({
    'Content-Type': 'application/json; charset=UTF-8'
  })
});

fetch(request)
  .then(function() {
   window.location.href = "http://127.0.0.1:8000"
  }).catch(error => console.error('Error fetching:', error));





  });
});

});

});


