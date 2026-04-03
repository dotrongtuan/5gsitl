#include <fstream>
#include <map>
#include <sstream>
#include <string>

#include <omnetpp.h>

using namespace omnetpp;

class ExternalStateBridge : public cSimpleModule {
  private:
    cMessage *tick = nullptr;

    std::map<std::string, std::string> readState(const char *path) {
        std::ifstream in(path);
        std::map<std::string, std::string> values;
        std::string line;
        while (std::getline(in, line)) {
            auto pos = line.find('=');
            if (pos == std::string::npos) {
                continue;
            }
            values[line.substr(0, pos)] = line.substr(pos + 1);
        }
        return values;
    }

    void label(const char *moduleName, const std::string& baseText, const std::string& state) {
        cModule *target = getParentModule()->getSubmodule(moduleName);
        if (!target) {
            return;
        }
        std::stringstream ss;
        ss << baseText << "\\n" << state;
        target->getDisplayString().setTagArg("t", 0, ss.str().c_str());
    }

    void refresh() {
        auto values = readState(par("stateFile").stringValue());
        label("amf", "5GC\\nAMF", values["component.core"]);
        label("smf", "5GC\\nSMF", values["component.core"]);
        label("upf", "5GC\\nUPF", values["component.core"]);
        label("udm", "5GC\\nUDM", values["component.core"]);
        label("nssf", "5GC\\nNSSF", values["component.core"]);
        label("pcf", "5GC\\nPCF", values["component.core"]);
        label("gnb", "Virtual RAN\\ngNB", values["component.gnb"]);

        std::stringstream ueText;
        ueText << "Virtual RAN\\nUE\\n" << values["attach_state"] << "\\n" << values["ue_ip"];
        cModule *ue = getParentModule()->getSubmodule("ue");
        if (ue) {
            ue->getDisplayString().setTagArg("t", 0, ueText.str().c_str());
        }

        label("zmqDownlink", "Virtual RF\\nZMQ DL", values["component.gnb"]);
        label("zmqUplink", "Virtual RF\\nZMQ UL", values["component.gnb"]);
        label("channel", "Channel\\nGNU Radio", values["component.channel"]);
        label("captureSubsystem", "Measure\\nCapture", values["component.capture"]);
        label("scenarioSelector", "Control\\nScenario", values["active_scenario"]);
        label("sliceSelector", "Control\\nSlice", values["active_slice"]);
        label("testcaseRunner", "Control\\nTestcase", values["active_testcase"]);

        std::stringstream metrics;
        metrics << "RTT(avg): " << values["metric.avg_rtt_ms"]
                << " ms | p95: " << values["metric.p95_rtt_ms"]
                << " | p99: " << values["metric.p99_rtt_ms"]
                << " | loss: " << values["metric.packet_loss_pct"]
                << "% | jitter: " << values["metric.jitter_ms"]
                << " ms | NR: " << values["nr_profile"]
                << " | CH: " << values["channel_profile"];
        getParentModule()->getDisplayString().setTagArg("t", 0, metrics.str().c_str());
    }

  protected:
    void initialize() override {
        tick = new cMessage("poll-state");
        scheduleAt(simTime(), tick);
    }

    void handleMessage(cMessage *msg) override {
        if (msg == tick) {
            refresh();
            scheduleAt(simTime() + par("pollInterval"), tick);
        }
    }

    void finish() override {
        cancelAndDelete(tick);
        tick = nullptr;
    }
};

Define_Module(ExternalStateBridge);
