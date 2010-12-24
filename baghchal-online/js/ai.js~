/**
 * @author saroj
 */
function validmove(r1, c1, r2, c2) {
    // no check for pieces here...do it manually
    // this is useful because valimove is used for tiger, goat, && ai moves
    
    if (distance(r1, c1, r2, c2)<2) {
	if ((r1+c1)%2==0) {
	    return 1;
	} else {
	    if (distance(r1, c1, r2, c2)==1) {
		return 1;
	    }
	}
    }
    return 0;
}

function validjump(r1, c1, r2, c2) {
    // (midRow, midCol) should be a goat; two end points can have any piece 
    // || none so check it manually while using validjump
    midRow = (r1+r2)/2;
    midCol = (c1+c2)/2;
    if (distance(r1, c1, midRow, midCol)==0.5*distance(r1, c1, r2, c2)) {
	if (isGoat(midRow, midCol) && validmove(r1, c1, midRow, midCol) && validmove(midRow, midCol, r2, c2)) {
	    return 1;
	}
    }
}

function bestMoveTiger() {
    maxPts = 0;
    maxr1 = 0; maxc1 = 0; maxr2 = 0; maxc2 = 0;
    for(r1=0; r1<5; ++r1) {
	for(c1=0; c1<5; ++c1) {
	    for(r2=0; r2<5; ++r2) {
		for(c2=0; c2<5; ++c2) {
		    pts = 0;
		    if (isTiger(r1, c1) && isBlank(r2, c2)) {
			if (validjump(r1, c1, r2, c2)==1) {
			    pts = pts + 1000;
			    pts = pts + tigerSecondary(r1, c1, r2, c2);
			}
			if (validmove(r1, c1, r2, c2)==1) {
			    pts = pts + 20;
			    pts = pts + tigerSecondary(r1, c1, r2, c2);
			}
			if (pts>maxPts) {
			    maxr1 = r1;
			    maxc1 = c1;
			    maxr2 = r2;
			    maxc2 = c2;
			    maxPts = pts;
			}
			// implement random if you wish for equal ones.
		    }
		}
	    }
	}
    }
    
    if (maxPts!=0) {
	pieces[maxr1][maxc1] = 0;
	pieces[maxr2][maxc2] = 1;
	if (maxPts>1000) {
	    pieces[(maxr1+maxr2)/2][(maxc1+maxc2)/2]=0;
	    goatsEaten = goatsEaten + 1;
	}
	turn = 2;
    }
}

function tigerSecondary(r1, c1, r2, c2) {
    tmp = 0;
    for(i=r2-2; i<r2+3; i=i+2) {
	for(j=c2-2; j<c2+3; j=j+2) {
	    if(validjump(r2, c2, i, j)==1 && isBlank(i, j)) {
		tmp = tmp + 100;
	    }
	}
    }
    for(i=r1-2; i<r1+3; i=i+2) {
	for(j=c1-2; j<c1+3; j=j+2) {
	    if(validjump(i, j, r1, c1)==1 && isTiger(i, j)) {
		tmp = tmp + 50;
	    }
	}
    }          
    if((r2+c2)%2==0) {
	tmp = tmp + 10;
    }
    if(r2==0 || r2==4 || c2==0 || c2==4) {
	tmp = tmp +4;
    }
    
    tmp = tmp + Math.abs(Math.pow(r2-2, 3)+Math.pow(c2-2, 3));
    return tmp;
}

function isTiger(row, col) {
    if (Math.round(row)==row && Math.round(col)==col) {
	if ((row>=0 && row <5) && (col>=0 && col<5) && pieces[row][col]==1) {
	    return true;
	}
    }
}

function isGoat(row, col) {
    if (Math.round(row)==row && Math.round(col)==col) {
	if ((row>=0 && row <5) && (col>=0 && col<5) && pieces[row][col]==2) {
	    return true;
	}
    }
}

function isBlank(row, col) {
    if (Math.round(row)==row && Math.round(col)==col) {
	if ((row>=0 && row <5) && (col>=0 && col<5) && pieces[row][col]==0) {
	    return true;
	}
    }
}

function distance(x1, y1, x2, y2) {
    return (Math.sqrt(Math.pow((x2-x1),2)+Math.pow((y2-y1), 2)));
}	