fetch('/api/scan')
.then(response => response.json())
.then(result => {
  console.log('Success:', result);
  
  result.networks.forEach(function(e, i) {
      document.getElementById("networks").add(new Option(e.name, e.name))
  });
})
.catch(error => {
  console.error('Error:', error);
});