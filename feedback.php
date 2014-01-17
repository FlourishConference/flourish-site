<!DOCTYPE html>
<html>
<head>

	<title> Flourish! </title>
	<link href="flourishconf.com/2014/images/favicon.gif" rel="shortcut icon">
	<link rel="stylesheet" href="css/default.css" type="text/css" />

</head>
<body>
	<div id="main-container" >
		<?php
			include("header.php");
			include("sidebar.php");
		?>
		<div id="main-body">

			<h1 class="content-title">Feedback for Flourish! Conference 2014</h1>
			<br />
			<form action="http://flourishconf.com/2014/feedback.php" method="POST">
				<strong>Name (optional)</strong>:<br />
				<input type="text" name="name" value="" />
				<br /><br />
				
				<strong>E-Mail (optional)</strong>:<br />
				<input type="email" name="email" value="" />
				<br /><br />
				
				<strong>Message</strong>:<br />
				<textarea name="message"></textarea>
				<br /><br />

				<input type="submit" name="submit" value="Submit Feedback" />
			</form>
		</div>
		<br />
	</div>
	<?php
		include("footer.php");
	?>
</body>

</html>