package sitl;

import sitl.ExternalStateBridge;
import sitl.VisualNode;

network SITLTopology
{
    parameters:
        @display("bgb=1700,940");
    submodules:
        bridge: ExternalStateBridge {
            parameters:
                stateFile = default("../../outputs/runtime/omnetpp.env");
                pollInterval = 1s;
                @display("p=845,40;i=block/cogwheel;t=State Bridge");
        }
        amf: VisualNode { parameters: label = "5GC\\nAMF"; @display("p=180,140;i=block/process"); }
        smf: VisualNode { parameters: label = "5GC\\nSMF"; @display("p=180,230;i=block/process"); }
        upf: VisualNode { parameters: label = "5GC\\nUPF"; @display("p=180,320;i=block/process"); }
        udm: VisualNode { parameters: label = "5GC\\nUDM"; @display("p=180,410;i=block/process"); }
        nssf: VisualNode { parameters: label = "5GC\\nNSSF"; @display("p=180,500;i=block/process"); }
        pcf: VisualNode { parameters: label = "5GC\\nPCF"; @display("p=180,590;i=block/process"); }

        gnb: VisualNode { parameters: label = "Virtual RAN\\ngNB"; @display("p=520,240;i=device/antennatower"); }
        ue: VisualNode { parameters: label = "Virtual RAN\\nUE"; @display("p=520,520;i=device/laptop"); }

        zmqDownlink: VisualNode { parameters: label = "Virtual RF\\nZMQ DL"; @display("p=820,200;i=block/queue"); }
        zmqUplink: VisualNode { parameters: label = "Virtual RF\\nZMQ UL"; @display("p=820,560;i=block/queue"); }

        channelSim: VisualNode { parameters: label = "Channel\\nGNU Radio"; @display("p=1080,380;i=block/wifirouter"); }

        latencyMonitor: VisualNode { parameters: label = "Measure\\nLatency"; @display("p=1360,180;i=block/chart"); }
        kpiCollector: VisualNode { parameters: label = "Measure\\nKPI"; @display("p=1360,280;i=block/chart"); }
        captureSubsystem: VisualNode { parameters: label = "Measure\\nCapture"; @display("p=1360,380;i=block/app"); }
        logExporter: VisualNode { parameters: label = "Measure\\nLogs"; @display("p=1360,480;i=block/table"); }

        scenarioSelector: VisualNode { parameters: label = "Control\\nScenario"; @display("p=1360,620;i=block/control"); }
        sliceSelector: VisualNode { parameters: label = "Control\\nSlice"; @display("p=1360,710;i=block/control"); }
        testcaseRunner: VisualNode { parameters: label = "Control\\nTestcase"; @display("p=1360,800;i=block/control"); }
        usecaseManager: VisualNode { parameters: label = "Control\\nUse Case"; @display("p=1560,665;i=block/control"); }
        reportGenerator: VisualNode { parameters: label = "Control\\nReport"; @display("p=1560,785;i=block/control"); }
    connections allowunconnected:
        amf.io++ <--> { @display("ls=blue,2"); } <--> smf.io++;
        smf.io++ <--> { @display("ls=green,2"); } <--> upf.io++;
        amf.io++ <--> { @display("ls=blue,2"); } <--> gnb.io++;
        upf.io++ <--> { @display("ls=green,2"); } <--> gnb.io++;
        gnb.io++ <--> { @display("ls=red,2"); } <--> zmqDownlink.io++;
        gnb.io++ <--> { @display("ls=red,2"); } <--> zmqUplink.io++;
        zmqDownlink.io++ <--> { @display("ls=red,2"); } <--> channelSim.io++;
        zmqUplink.io++ <--> { @display("ls=red,2"); } <--> channelSim.io++;
        channelSim.io++ <--> { @display("ls=green,2"); } <--> ue.io++;
        ue.io++ <--> { @display("ls=orange,2"); } <--> latencyMonitor.io++;
        ue.io++ <--> { @display("ls=orange,2"); } <--> kpiCollector.io++;
        upf.io++ <--> { @display("ls=orange,2"); } <--> captureSubsystem.io++;
        amf.io++ <--> { @display("ls=orange,2"); } <--> logExporter.io++;
        scenarioSelector.io++ <--> { @display("ls=purple,2"); } <--> testcaseRunner.io++;
        sliceSelector.io++ <--> { @display("ls=purple,2"); } <--> testcaseRunner.io++;
        testcaseRunner.io++ <--> { @display("ls=purple,2"); } <--> reportGenerator.io++;
        usecaseManager.io++ <--> { @display("ls=purple,2"); } <--> sliceSelector.io++;
        usecaseManager.io++ <--> { @display("ls=purple,2"); } <--> scenarioSelector.io++;
}
