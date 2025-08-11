from graph_api import Graph
import json

script = """
    (function renderMainView(nodeData, links)
    {
        const svg = d3.select("svg");
        const width = svg.node().getBoundingClientRect().width
        const height = svg.node().getBoundingClientRect().height

        const nodes = nodeData.map(node => ({"id": node.id}))

        // Create a simulation to position nodes
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink().id(d => d.id).strength(1))
            .force("charge", d3.forceManyBody().strength(-20000))
            .force("collide", d3.forceCollide().strength(200).radius((node) => Math.max(node.width, node.height)).iterations(1))
            .on("tick", ticked);
        simulation.force('link').links(links)


        const linkElements = svg.append("g")
            .selectAll(".link")
            .data(links)
            .enter().append("line")
            .attr("stroke", "black")
            .attr("stroke-width", "3px");

        function nodeToHTML(node){
            let html = `<div style='padding:10px; border:1px solid black;text-align: center;background-color: orange; border-radius: 10px 10px 0px 0px;'>${node['id']}</div>`
            let nodeDTO = nodeData.find(node1 => node1['id'] == node['id'])
            let attributeText = Object.keys(nodeDTO).filter(key => key != "id").map(key => "<p style='white-space:nowrap'>" + key + ": " + nodeDTO[key] + "</p>").join("<br/>")
            html += `<div style='background-color:#fad7a0; border-radius: 0px 0px 10px 10px; padding:10px; border:1px solid black;'>${attributeText}</div>`
            return html
        }

        const nodeElements = svg.append("g")
            .selectAll('foreignObject')
            .data(nodes)
            .enter().append('foreignObject')
            .attr("width", "1")
            .attr("height", "1")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended))
            .append("xhtml:div")
            .attr("style", "width:fit-content;")
            .attr("nodeId", node => node['id'])
            .html(node => nodeToHTML(node))


        svg.selectAll('div[nodeId]').each((node) => {
            let nodeDiv = document.querySelector(`div[nodeId='${node.id}']`)
            node.width = nodeDiv.offsetWidth
            node.height = nodeDiv.offsetHeight
        })

        svg.selectAll('foreignObject')
            .attr("width", node => node.width)
            .attr("height", node => node.height)

        svg.call(d3.zoom()
            // .extent([[0, 0], [width, height]])
            // .scaleExtent([1, 8])
            .on("zoom", zoomed));

        function zoomed({transform}) {
            d3.selectAll("svg g").attr("transform", transform);
        }

        // Function to update positions
        function ticked() {
            linkElements
                .attr("x1", d => d.source.x + d.source.width/2)
                .attr("y1", d => d.source.y + d.source.height/2)
                .attr("x2", d => d.target.x + d.target.width/2)
                .attr("y2", d => d.target.y + d.target.height/2);

            svg.selectAll("foreignObject")
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        }

        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }
            
        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }
            
        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }
    })(NODES, LINKS)
"""
class BlockVisualizer():
    def visualize_graph(self, g: Graph)->str:
        parsedNodes = []
        for node in g._vertices.values():
            parsedNodes.append(node._attributes)

        parsedLinks = []
        for source, targets in g._edges.items():
            for target in targets:
                parsedLinks.append({"source": source, "target": target})
        
        return script.replace("NODES", json.dumps(parsedNodes)).replace("LINKS", json.dumps(parsedLinks))