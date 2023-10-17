let bArchive = true;
document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
	document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
	document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
	document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
	document.querySelector('#compose').addEventListener('click', compose_email);
	document.querySelector('#sendbtn').addEventListener('click', function () {submitmail();return false;} );
	document.querySelector('#btnarchive').addEventListener('click', function () {archivemail(txtmailid.value, bArchive);return false;} );
			
  

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {
  //~ alert(document.querySelector('#emails-view').style.display);
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = document.querySelector('#emails-list').style.display = document.querySelector('#mail-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
  

}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = document.querySelector('#emails-list').style.display = 'block';
  document.querySelector('#compose-view').style.display = document.querySelector('#mail-view').style.display = 'none';
  
  // Show the mailbox name
	document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
	if(mailbox == 'inbox'){
		bArchive = true;
		document.querySelector('#emails-list').innerHTML = '<div class="row emailhead"><div class="col-sm h6">Sender</div><div class="col-sm h6">Subject</div><div class="col-sm h6 colright">Sent</div></div>	';
		fetch('/emails/inbox')
		.then(response => response.json())
		.then(emails => {
			// Print emails
			//console.log(emails);
			emails.forEach(function(item) {displayemaillist(item, true)});
			});
		document.querySelector('#btnarchive').value = "Archive";
	
	}
	else if(mailbox == 'sent'){
		bArchive = true;
		document.querySelector('#emails-list').innerHTML = '<div class="row emailhead"><div class="col-sm h6">To</div><div class="col-sm h6">Subject</div><div class="col-sm h6 colright">Sent</div></div>	';
		fetch('/emails/sent')
		.then(response => response.json())
		.then(emails => {
			// Print emails
			//console.log(emails);
			emails.forEach(function(item) {displayemaillist(item, false)});
			});	
	}
	else if(mailbox== 'archive'){
		bArchive = false;
		document.querySelector('#emails-list').innerHTML = '<div class="row emailhead"><div class="col-sm h6">Sender</div><div class="col-sm h6">Subject</div><div class="col-sm h6 colright">Sent</div></div>	';
		fetch('/emails/archive')
		.then(response => response.json())
		.then(emails => {
			// Print emails
			//console.log(emails);
			emails.forEach(function(item) {displayemaillist(item, false)});
			});
		document.querySelector('#btnarchive').value = "Restore";		
	};
	
}
function displayemaillist(email, inbox){

	let sEmlCol = "";
	let sClass = "";
	
	if(inbox){
		sEmlCol = email.sender;
	}
	else{
		sEmlCol = email.recipients;
	}
	if(email.read && inbox){
		sClass = "row emailrow read";
	}
	else{
		sClass = "row emailrow";
	}	
	
	x = document.querySelector('#emails-list');	x.innerHTML += `<div class="${sClass}" onclick=viewmail(${email.id});><div class="col-sm"> ${sEmlCol} </div><div class="col-sm"> ${email.subject} </div><div class="col-sm colright"> ${email.timestamp} </div></div>`;
}
function submitmail(){
	//~ alert("submit");
	fetch('/emails', {
		method: 'POST',
		body: JSON.stringify({
			recipients: document.querySelector('#compose-recipients').value,
			subject: document.querySelector('#compose-subject').value,
			body: document.querySelector('#compose-body').value
		})
	})
	.then(response => response.json())
	.then(result => {
		// Print result
		console.log(result);
	});
	load_mailbox('inbox');
}
function viewmail(mailid){
	document.querySelector('#emails-view').style.display = document.querySelector('#emails-list').style.display = 'none';
	document.querySelector('#mail-view').style.display = 'block';
	//alert(document.querySelector('#emails-view').innerHTML);
	if(document.querySelector('#emails-view').innerHTML.includes('Sent')){
		btnarchive.style.display = 'none';
	}
	else{
		btnarchive.style.display = '';
	}
	fetch(`/emails/${mailid}`)
		.then(response => response.json())
		.then(email => {
			// Print email
			//console.log(email);
			//~ lblFrom = document.querySelector('#lblFrom');
			lblFrom.innerHTML = email.sender;
			lblTo.innerHTML = email.recipients;
			lblSubject.innerHTML = email.subject;
			lblTimestamp.innerHTML = email.timestamp;
			txtMailBody.value = email.body;
			document.getElementById('txtmailid').value = mailid;
			//alert(txtmailid.value);
			// ... Mark as read ...
			fetch(`/emails/${mailid}`, {
			  method: 'PUT',
			  body: JSON.stringify({
				  read: true
			  })
			})
			
		});

}
function archivemail(mailid, archive){
	//alert(archive);
	fetch(`/emails/${mailid}`, {
		method: 'PUT',
		body: JSON.stringify({
		archived: archive
		})
	})
	.then(response => load_mailbox('inbox'));

	//load_mailbox('inbox');
}
