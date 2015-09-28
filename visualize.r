# Skeleton for program to process data from csv file and visualize it

main = function(){
  # ****** Module vars *******
  Mcsvname = "px.hotelnights.csv"
  #***************************

  # Logical flow of program
  df = csvtodf(Mcsvname)
  print(df)
}

csvtodf = function(fname){
  # Reads csv file (produced from data on px server) into data.frame.
  df=read.csv2(fname,header=T,sep=",",dec=".",as.is=T,encoding='UTF-8')
  return(df)
}
