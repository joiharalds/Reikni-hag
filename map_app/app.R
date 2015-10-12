library(zoo)
library(jsonlite)
library(leaflet)
library(shiny)
library(RColorBrewer)

# --- Read in the data and prepare the dataframe ---

# read in the data
tourist_data = read.csv("px.hotelnights.csv", header=TRUE, sep=",", na.strings="..")

# filter out the unnecessary rows where Mánuður = "Allir"
tourist_data <- tourist_data[tourist_data$Mánuður != "Allir",]


# change the month names to english
month_names_isl <- c("janúar", "febrúar", "mars", "apríl", "maí", "júní", "júlí",
		    "ágúst", "september", "október", "nóvember", "desember")
month_names_en <- c("January", "February", "March", "April", "May", "June", "July",
		    "August", "September", "October", "November", "December")

translate <- function(from_lang, to_lang){
	function(from_name){
		return (to_lang[match(tolower(from_name), from_lang)])
	}
}
# returns a function to translate between two languages
month_names_to_en <- translate(month_names_isl, month_names_en)


# append combined year/month column to the right
tourist_data <- cbind(Dagsetning = as.yearmon(
					      paste(
						    tourist_data$Ár, 
						    month_names_to_en(tourist_data$Mánuður), 
						    sep = ","),
					      format = "%Y,%B"),
		      tourist_data)

# remove the unnecessary "Ár" and "Mánuður" columns
tourist_data[c("Ár", "Mánuður")] <- list(NULL)

# rename the headers to english
names(tourist_data)[names(tourist_data) == 'Dagsetning'] <- 'Date'
names(tourist_data)[names(tourist_data) == 'Þjóðerni'] <- 'Nationality'
names(tourist_data)[names(tourist_data) == 'Landsvæði'] <- 'Region'
names(tourist_data)[names(tourist_data) == 'Value0'] <- 'Number'

# order by date
tourist_data <- tourist_data[order(tourist_data$Date),]


# --- Processing ---

# add logarithm of number of tourists
tourist_data$Log <- log(tourist_data$Number)

# List of nationalities
nationalities <- unique(tourist_data$Nationality)

# List of time values
time_range <- unique(tourist_data$Date)
time_min <- tourist_data$Date[[1]]
time_max <- tail(tourist_data$Date, 1)




# --- Preparing for shiny --- 

# read in the geoJSON file
geojson <- readLines("../iceland-geodata/regions/1000/iceland_regions.geojson", warn = FALSE) %>%
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
		    absolutePanel(top = 10, right = 13,
				  sliderInput(inputId="time", label="Time", min = 1, max = length(time_range), value=1, step=1),
				  selectInput(inputId="nat", label="Nationality",choices= as.character(nationalities)),
				  selectInput("colors", "Color Scheme",rownames(subset(brewer.pal.info, category %in% c("seq", "div")))),
				            checkboxInput("legend", "Show legend", TRUE)
				  )
		    )

server <- function(input, output) {

	reacVals <- reactiveValues()
	reacVals$geo <- geojson
	colorPal <- reactiveValues()
	PalValues <- reactiveValues()
# Create the colour palette
get_palette <- function(data) {
	colorNumeric(palette=input$colors, domain=data$Log)
}
PalVal <- reactive({
	tourist_data[(tourist_data$Nationality == input$nat)]$Log
})
Pal <- reactive({
	get_palette(tourist_data[(tourist_data$Nationality == input$nat),])
})

get_color <- function(data, time, region_name, pal) {
	colorPal = get_palette(data)

	return(colorPal(data[(data$Region == region_name) & (data$Date == time),]$Log))
}
# Add a properties$style list to each feature (each region)
	observe(priority=1, {
		reacVals$geo$features <- lapply(reacVals$geo$features, function(region) {
					   region_name = region$properties$Name
	if (region_name == "Vesturland" | region_name == "Vestfirðir") {
		region_name = "Vesturland, Vestfirðir"
	} else if (region_name == "Höfuðborgarsvæðið" | region_name == "Reykjanes") {
		region_name = "Höfuðborgarsvæði"
	}
	PalValues = tourist_data[(tourist_data$Nationality == input$nat),]
	 region$properties$style <- list(
					 fillColor = get_color(PalValues, time_range[[input$time]], region_name)
					   )
				  return(region)
				  })
	output$my_map <- renderLeaflet({
		leaflet() %>% setView(lng = -19.000, lat = 65.000, zoom = 6.20) %>% # zoom = 6.20
		addTiles() %>% addLegend(pal =Pal(), values = tourist_data[(tourist_data$Nationality == input$nat),]$Log)
	})
})
	observeEvent(input$time, {
		leafletProxy("my_map") %>% clearGeoJSON() %>% addGeoJSON(reacVals$geo)
	})

	observeEvent(input$nat, {
		leafletProxy("my_map") %>% clearGeoJSON() %>% addGeoJSON(reacVals$geo)
	})

}


shinyApp(ui, server)
