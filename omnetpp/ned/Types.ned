simple VisualNode
{
    parameters:
        string label = default("");
        @class(VisualNode);
    gates:
        inout io[];
}

simple ExternalStateBridge
{
    parameters:
        string stateFile;
        double pollInterval @unit(s) = default(1s);
        @class(ExternalStateBridge);
}
