for par in *par;
do
    echo $par
    psrj=`basename ${par%.*}`
    python add_pn.py ${psrj}.par ${psrj}.tim ${psrj}_pn.tim
done
