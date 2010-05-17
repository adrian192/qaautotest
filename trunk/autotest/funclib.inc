<?php
require_once ('constants.inc');  // Probably don't need this.
require_once ('report.inc'); // All the report functions are here.
$LIVE=TRUE;

function javascript_header () {
	?>
	<script type="text/javascript">
	var openImg = new Image();
	openImg.src = "ArrowDn.gif";
	var closeImg = new Image();
	closeImg.src = "ArrowRt.gif";

	function testScript () {
		alert ("Testing");
	}

	function checkAll (fname, chkbox) {
		var val = chkbox.checked;
		for (var i=0;i<fname.length;i++) {
			var e = fname.elements[i];
			if (e.name !='allbox') {
				e.checked=val;
			}
		}
	}

	function checkOne (fname, chkbox, chkname) {
		var val = chkbox.checked;
		var found = false;
		for (var i=0;i<frame.length;i++) {
			var e=fname.elements[i];
			var c=e.value.indexOf(",");
			if (c > 0) {
				var x = e.value.substr(0,c);
				if (x==chkname) {
					found = true;
					e.checked=val;
				} else {
					if (found) {
						return;
					}
				}
			}
		}
	}
	</script>
	<?php
}



###############################
# Cascading Style sheet header
###############################
function style_header() {
    ?>  
    <style type="text/css">
    body{
    font: 10pt Verdana,sans-serif;
    color: darkblue;
    }
    .trigger{
    cursor: pointer;
    cursor: hand;
    }
    .branch{
    display: none;
    margin-left: 10px;
    }
    </style>
    <?php
}

###############################
# Database access functions
###############################
function connect_db () {
	error_reporting (E_ALL);
	$ini_array = parse_ini_file("database.ini");
	$link = mysql_pconnect ($ini_array["host"], $ini_array["user"], $ini_array["password"]);
	if (!$link) {
		die ('Could not connect db: '.mysql_error());
	}
	$db_selected = mysql_select_db ($ini_array["db_name"], $link);
	if (!$db_selected) {
		die ('Could not use db autotest: '.mysql_error());
	}
}


function make_page_selector ($page_id) {
	$PAGES=array();
	$PAGES[1] = "Reports";
	$PAGES[2] = "Management";
//TODO:	$PAGES[2] = "Run Test";
	?>
	<select name="page_display" onchange=submit();>
	<?php
	foreach (array_keys($PAGES) as $id) {
		$selected="";
		if ($page_id == $id) {
			$selected = "selected";
		}
		echo "<option value=\"{$id}\" {$selected}>{$PAGES[$id]}</option>\n";
	}
	?>
	</select>
	<?php
}

function make_report_header () {
	?>
	<html><head><title>Auto Test Report Header</title>
	<?php style_header (); ?>
	</head>
	<body>
	<table border=0 cellpadding=0, width=100%>
		<tr><td valign="top">
            <form action="<?=$_SERVER['PHP_SELF']?>" name="task_form" method="post" target="_top">
                <table border=0 width="100%">
                    <tr>
                        <td valign="top"> <?php make_page_selector(1); ?> </td>
                    </tr>
                    <tr></tr>
                </table>
            </form>
        </td></tr>
    </table>
    </body>
    </html>
    <?php
}



function report_layout ($padding) {
	global $COLORS;
	$hd=60+$padding;
	?>
	<html><head><title>Auto Test Report</title>
	<?php javascript_header (); ?>
	<?php style_header (); ?>
<?php /*
	<frameset rows="<?=$hd?>,*">
		<frame src=<?=$_SERVER['PHP_SELF']?>?frame=page1_header name=page1_header scrolling="no">
*/?>
		<frameset cols="30%,*">
			<frame src=<?=$_SERVER['PHP_SELF']?>?frame=report_left name=report_left>
			<frame src=<?=$_SERVER['PHP_SELF']?>?frame=report_right name=report_right>
		</frameset>
<?php /*
	</frameset>
*/?>
	</head>
	<?php
}

function management_layout ($padding) {
	global $COLORS;
	$hd=60+$padding;
	?>
	<html><head><title>Auto Test Management</title>
	<?php javascript_header (); ?>
	<?php style_header (); ?>
	<frameset cols="35%,*">
		<frame src=<?=$_SERVER['PHP_SELF']?>?frame=management_left name=management_left>
		<frame src=<?=$_SERVER['PHP_SELF']?>?frame=management_right name=management_right>
	</frameset>
	</head>
	<?php
}

function make_header () {
	global $COLORS;
	?>
	<html><head><title>Header Frame</title>
	<?php style_header (); // set the header font/style/etc ?>
	</head>
	<body>
	<table width="100%" border="1">
		<tr><td valign="top">
			<form action="<?=$_SERVER['PHP_SELF']?>" name="task_form" method="post" target="_top">
				<table border=0 width="100%">
					<tr>
						<td valign="top"> <?php make_page_selector(1); ?> </td>
					</tr>
					<tr></tr>
				</table>
			</form>
		</td></tr>
	</table>
	</body>
	</html>
	<?php
}

?>
