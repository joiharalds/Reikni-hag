library(zoo)
library(jsonlite)
library(leaflet)
library(shiny)

# --- Read in the data and prepare the dataframe ---

# read in the data
tourist_data = read.csv("pxeng.hotelnights.csv", header=TRUE, sep=",", na.strings="..")

# filter out the unnecessary rows where Mánuður = "Allir"
tourist_data <- tourist_data[tourist_data$Month != "Total",]

# append combined year/month column to the right
tourist_data <- cbind(Date = as.yearmon(
                                        paste(
                                              tourist_data$Year, 
                                              tourist_data$Month, 
                                              sep = ","),
                                        format = "%Y,%B"),
		      tourist_data)

# remove the unnecessary "Year" and "Month" columns
tourist_data[c("Year", "Month")] <- list(NULL)

# rename the header
names(tourist_data)[names(tourist_data) == 'Dagsetning'] <- 'Date'
names(tourist_data)[names(tourist_data) == 'Þjóðerni'] <- 'Citizenship'
names(tourist_data)[names(tourist_data) == 'Landsvæði'] <- 'Region'
names(tourist_data)[names(tourist_data) == 'Value0'] <- 'Number'

# order by date
tourist_data <- tourist_data[order(tourist_data$Date),]


# --- Processing ---

# add logarithm of number of tourists
tourist_data$Log <- log(tourist_data$Number)

# List of citizenship
citizenship <- unique(tourist_data$Citizenship)

# List of time values
time_range <- unique(tourist_data$Date)
time_min <- tourist_data$Date[[1]]
time_max <- tail(tourist_data$Date, 1)


# Create the colour palette
get_palette <- function(data) {
	colorNumeric(palette="Greens", domain=data$Log)
}

get_color <- function(data, time, region_name, pal) {
	data_name = region_name # name of the region in the data
	if (region_name == "Vesturland" | region_name == "Vestfirðir") {
		data_name = "Vesturland, Vestfirðir"
	} else if (region_name == "Höfuðborgarsvæðið" | region_name == "Reykjanes") {
		data_name = "Höfuðborgarsvæði"
	}
	pal = get_palette(data)

	return(pal(data[(data$Region == data_name) & (data$Date == time),]$Log))
}


# --- Preparing for shiny --- 

# read in the geoJSON file
geojson <- readLines("iceland-geodata/regions/1000/iceland_regions.geojson", warn = FALSE) %>%
paste(collapse = "\n") %>%
fromJSON(simplifyVector = FALSE)

# Default styles for all features
geojson$style = list(
		     weight = 1,
		     color = "#555555",
		     opacity = 1,
		     fillOpacity = 0.8
		     )

# Shiny processing, we specify the UI and the server.
ui <- bootstrapPage(
		    tags$style(type = "text/css", "html, body {width:90%;height:90%}"),
		    leafletOutput("my_map", width = "90%", height = "90%"),
		    absolutePanel(top = 10, right = 10,
				  sliderInput(inputId="time", label="Time", min = 1, max = length(time_range), value=1, step=1),
				  selectInput(inputId="nat", label="Citizenship",
					      choices= as.character(citizenship))
				  )
		    )

server <- function(input, output) {

	reacVals <- reactiveValues()
	reacVals$geo <- geojson


	# Add a properties$style list to each feature (each region)
	observe(priority=1, {
		reacVals$geo$features <- lapply(reacVals$geo$features, function(region) {
					   region_name = region$properties$Name
					   region$properties$style <- list(
									   fillColor = get_color(tourist_data[(tourist_data$Citizenship == input$nat),], time_range[[input$time]], region$properties$Name)
									   )
					   region
				  })
	})


	output$my_map <- renderLeaflet({
		leaflet() %>% setView(lng = -19.000, lat = 65.000, zoom = 6.20) %>% # zoom = 6.20
		addTiles() #%>% addGeoJSON(geojson)
	})

	observeEvent(input$time, {
		leafletProxy("my_map") %>% clearGeoJSON() %>% addGeoJSON(reacVals$geo)
	})

	observeEvent(input$nat, {
		leafletProxy("my_map") %>% clearGeoJSON() %>% addGeoJSON(reacVals$geo)
	})

}


shinyApp(ui, server)
