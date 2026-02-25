import './ThinkingIndicator.css'

export default function ThinkingIndicator() {
    return (
        <div className="flex justify-start">
            <div className="thinking-container">
                <div className="thinking-layout">
                    {/* Animated generator illustration — pure CSS */}
                    <div className="generator">
                        {/* Generator body */}
                        <div className="gen-body">
                            {/* Vent lines */}
                            <div className="gen-vents">
                                <div className="vent" />
                                <div className="vent" />
                                <div className="vent" />
                            </div>

                            {/* Spinning turbine */}
                            <div className="turbine">
                                <div className="turbine-blade-group">
                                    <div className="blade blade-h" />
                                    <div className="blade blade-v" />
                                    <div className="blade blade-d1" />
                                    <div className="blade blade-d2" />
                                </div>
                                <div className="turbine-center" />
                            </div>

                            {/* Panel lights */}
                            <div className="panel-lights">
                                <div className="panel-light light-green" />
                                <div className="panel-light light-amber" />
                            </div>
                        </div>

                        {/* Exhaust stack */}
                        <div className="exhaust-stack">
                            <div className="exhaust-cap" />
                        </div>

                        {/* Smoke puffs */}
                        <div className="smoke-group">
                            <div className="smoke s1" />
                            <div className="smoke s2" />
                            <div className="smoke s3" />
                        </div>

                        {/* Energy sparks */}
                        <div className="spark spark-1" />
                        <div className="spark spark-2" />
                        <div className="spark spark-3" />
                        <div className="spark spark-4" />

                        {/* Pulsing energy rings */}
                        <div className="energy-ring ring-1" />
                        <div className="energy-ring ring-2" />
                    </div>

                    <div className="thinking-text-group">
                        <span className="thinking-label">
                            Generating
                            <span className="dot d1">.</span>
                            <span className="dot d2">.</span>
                            <span className="dot d3">.</span>
                        </span>
                        <span className="thinking-sub">
                            Searching documents &amp; crafting response
                        </span>
                    </div>
                </div>
            </div>
        </div>
    )
}
